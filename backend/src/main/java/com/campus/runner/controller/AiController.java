package com.campus.runner.controller;

import com.alibaba.fastjson.JSONObject;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.Map;
import java.util.concurrent.Executors;

@CrossOrigin
@RestController
@RequestMapping("/api/ai")
public class AiController {

    private static final MediaType TEXT_PLAIN_UTF8 = new MediaType("text", "plain", StandardCharsets.UTF_8);

    @Value("${ai.service.url:http://127.0.0.1:8000}")
    private String aiServiceUrl;

    @PostMapping(value = "/ask", produces = MediaType.TEXT_EVENT_STREAM_VALUE + ";charset=UTF-8")
    public SseEmitter ask(@RequestBody Map<String, Object> request) {
        String message = request.get("message") == null ? null : String.valueOf(request.get("message"));

        if (message == null || message.trim().isEmpty()) {
            SseEmitter emitter = new SseEmitter();
            try {
                emitter.send(SseEmitter.event().data("错误: message 不能为空", TEXT_PLAIN_UTF8));
                emitter.complete();
            } catch (IOException e) {
                emitter.completeWithError(e);
            }
            return emitter;
        }

        SseEmitter emitter = new SseEmitter(Long.MAX_VALUE);

        Executors.newSingleThreadExecutor().submit(() -> {
            HttpURLConnection conn = null;
            try {
                URL url = new URL(aiServiceUrl + "/chat");
                conn = (HttpURLConnection) url.openConnection();
                conn.setRequestMethod("POST");
                conn.setRequestProperty("Content-Type", "application/json; charset=UTF-8");
                conn.setRequestProperty("Accept", "text/event-stream");
                conn.setDoOutput(true);
                conn.setDoInput(true);

                JSONObject payload = new JSONObject();
                payload.put("message", message);

                Object userId = request.get("user_id");
                if (userId == null) {
                    userId = request.get("userId");
                }
                if (userId != null) {
                    payload.put("user_id", String.valueOf(userId));
                }

                Object history = request.get("history");
                if (history != null) {
                    payload.put("history", history);
                }

                try (OutputStream os = conn.getOutputStream()) {
                    os.write(payload.toJSONString().getBytes(StandardCharsets.UTF_8));
                }

                int responseCode = conn.getResponseCode();
                System.out.println("Python AI response status: " + responseCode);

                try (BufferedReader br = new BufferedReader(
                        new InputStreamReader(
                                responseCode >= 400 ? conn.getErrorStream() : conn.getInputStream(),
                                StandardCharsets.UTF_8))) {
                    String line;
                    while ((line = br.readLine()) != null) {
                        if (line.startsWith("data: ")) {
                            String data = line.substring(6);
                            if ("[DONE]".equals(data)) {
                                emitter.send(SseEmitter.event().data("[DONE]", TEXT_PLAIN_UTF8));
                                emitter.complete();
                                break;
                            }
                            emitter.send(SseEmitter.event().data(data, TEXT_PLAIN_UTF8));
                        }
                    }
                }
            } catch (Exception e) {
                System.out.println("Failed to call Python AI service: " + e.getMessage());
                try {
                    emitter.send(SseEmitter.event().data("错误: " + e.getMessage(), TEXT_PLAIN_UTF8));
                    emitter.complete();
                } catch (IOException ex) {
                    emitter.completeWithError(ex);
                }
            } finally {
                if (conn != null) {
                    conn.disconnect();
                }
            }
        });

        return emitter;
    }
}
