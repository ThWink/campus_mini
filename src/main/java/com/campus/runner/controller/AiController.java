package com.campus.runner.controller;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.servlet.mvc.method.annotation.SseEmitter;

import java.io.*;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.concurrent.Executors;

@CrossOrigin
@RestController
@RequestMapping("/api/ai")
public class AiController {

    @Value("${ai.service.url:http://127.0.0.1:8000}")
    private String aiServiceUrl;

    @PostMapping(value = "/ask", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public SseEmitter ask(@RequestBody java.util.Map<String, String> request) {
        String message = request.get("message");
        
        if (message == null || message.trim().isEmpty()) {
            SseEmitter emitter = new SseEmitter();
            try {
                emitter.send(SseEmitter.event().data("错误: message不能为空"));
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
                conn.setRequestProperty("Content-Type", "application/json");
                conn.setRequestProperty("Accept", "text/event-stream");
                conn.setDoOutput(true);
                conn.setDoInput(true);
                
                String jsonBody = "{\"message\": \"" + message + "\"}";
                try (OutputStream os = conn.getOutputStream()) {
                    os.write(jsonBody.getBytes(StandardCharsets.UTF_8));
                }

                int responseCode = conn.getResponseCode();
                System.out.println("Python响应状态: " + responseCode);
                
                try (BufferedReader br = new BufferedReader(
                        new InputStreamReader(
                                responseCode >= 400 ? conn.getErrorStream() : conn.getInputStream(), 
                                StandardCharsets.UTF_8))) {
                    String line;
                    while ((line = br.readLine()) != null) {
                        System.out.println("Python原始行: [" + line + "]");
                        if (line.startsWith("data: ")) {
                            String data = line.substring(6);
                            System.out.println("发送SSE: data: " + data);
                            if (data.equals("[DONE]")) {
                                emitter.send(SseEmitter.event().data("[DONE]"));
                                emitter.complete();
                            } else {
                                emitter.send(SseEmitter.event().data(data));
                            }
                        }
                    }
                }
                
            } catch (Exception e) {
                System.out.println("调用Python服务失败: " + e.getMessage());
                try {
                    emitter.send(SseEmitter.event().data("错误: " + e.getMessage()));
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
