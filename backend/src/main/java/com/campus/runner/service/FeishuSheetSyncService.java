package com.campus.runner.service;

import com.campus.runner.config.FeishuSheetProperties;
import com.campus.runner.entity.Order;
import com.campus.runner.entity.User;
import com.campus.runner.mapper.OrderMapper;
import com.campus.runner.mapper.UserMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;
import org.springframework.web.client.RestTemplate;

import java.time.Instant;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

@Service
public class FeishuSheetSyncService {

    private static final Logger log = LoggerFactory.getLogger(FeishuSheetSyncService.class);
    private static final DateTimeFormatter DATE_TIME_FORMATTER = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    private final FeishuSheetProperties properties;
    private final RestTemplate restTemplate;
    private final OrderMapper orderMapper;
    private final UserMapper userMapper;

    private String cachedTenantAccessToken;
    private Instant tokenExpiresAt = Instant.EPOCH;

    public FeishuSheetSyncService(FeishuSheetProperties properties,
                                  RestTemplate restTemplate,
                                  OrderMapper orderMapper,
                                  UserMapper userMapper) {
        this.properties = properties;
        this.restTemplate = restTemplate;
        this.orderMapper = orderMapper;
        this.userMapper = userMapper;
    }

    @Scheduled(cron = "${feishu.sheet.cron:0 5 0 * * ?}", zone = "${feishu.sheet.zone:Asia/Shanghai}")
    public void syncYesterdayBySchedule() {
        if (!properties.isEnabled()) {
            return;
        }

        LocalDate reportDate = LocalDate.now(ZoneId.of(properties.getZone())).minusDays(1);
        try {
            SyncReport report = syncDate(reportDate);
            log.info("Feishu sheet sync completed: {}", report);
        } catch (Exception e) {
            log.error("Feishu sheet sync failed for {}", reportDate, e);
        }
    }

    public SyncReport syncDate(LocalDate reportDate) {
        validateConfig();

        int orderRows = 0;
        int userRows = 0;

        if (properties.isSyncOrders()) {
            List<List<Object>> rows = buildOrderRows(reportDate);
            appendRows(properties.getOrderRange(), rows);
            orderRows = rows.size();
        }

        if (properties.isSyncUsers()) {
            List<List<Object>> rows = buildUserRows(reportDate);
            appendRows(properties.getUserRange(), rows);
            userRows = rows.size();
        }

        return new SyncReport(reportDate.toString(), orderRows, userRows);
    }

    private List<List<Object>> buildOrderRows(LocalDate reportDate) {
        LocalDateTime startTime = reportDate.atStartOfDay();
        LocalDateTime endTime = reportDate.plusDays(1).atStartOfDay();
        List<Order> orders = orderMapper.selectByCreateTimeRange(startTime, endTime);
        List<List<Object>> rows = new ArrayList<>();

        for (Order order : orders) {
            rows.add(row(
                    reportDate.toString(),
                    order.getId(),
                    order.getTaskId(),
                    order.getTitle(),
                    order.getDescription(),
                    order.getReward(),
                    order.getStatus(),
                    statusText(order.getStatus()),
                    order.getUserId(),
                    order.getPublisherName(),
                    order.getPublisherPhone(),
                    order.getRunnerId(),
                    order.getRunnerName(),
                    order.getRunnerPhone(),
                    formatDate(order.getCreateTime())
            ));
        }
        return rows;
    }

    private List<List<Object>> buildUserRows(LocalDate reportDate) {
        List<User> users = userMapper.selectAllUsers();
        List<List<Object>> rows = new ArrayList<>();

        for (User user : users) {
            rows.add(row(
                    reportDate.toString(),
                    user.getId(),
                    user.getUsername(),
                    user.getPhone(),
                    user.getRole(),
                    user.getStatus(),
                    formatDate(user.getCreateTime())
            ));
        }
        return rows;
    }

    private void appendRows(String range, List<List<Object>> rows) {
        if (rows.isEmpty()) {
            return;
        }

        String url = properties.getBaseUrl()
                + "/open-apis/sheets/v2/spreadsheets/"
                + properties.getSpreadsheetToken()
                + "/values_append?insertDataOption=INSERT_ROWS";

        HttpHeaders headers = new HttpHeaders();
        headers.setBearerAuth(getTenantAccessToken());
        headers.setContentType(MediaType.APPLICATION_JSON);

        Map<String, Object> valueRange = new LinkedHashMap<>();
        valueRange.put("range", range);
        valueRange.put("values", rows);

        Map<String, Object> body = new LinkedHashMap<>();
        body.put("valueRange", valueRange);

        Map<?, ?> response = restTemplate.postForObject(url, new HttpEntity<>(body, headers), Map.class);
        assertFeishuSuccess(response, "飞书表格追加失败");
    }

    private synchronized String getTenantAccessToken() {
        if (StringUtils.hasText(cachedTenantAccessToken) && Instant.now().isBefore(tokenExpiresAt.minusSeconds(60))) {
            return cachedTenantAccessToken;
        }

        String url = properties.getBaseUrl() + "/open-apis/auth/v3/tenant_access_token/internal";
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);

        Map<String, Object> body = new LinkedHashMap<>();
        body.put("app_id", properties.getAppId());
        body.put("app_secret", properties.getAppSecret());

        Map<?, ?> response = restTemplate.postForObject(url, new HttpEntity<>(body, headers), Map.class);
        assertFeishuSuccess(response, "获取飞书 tenant_access_token 失败");

        Object token = response.get("tenant_access_token");
        if (token == null || !StringUtils.hasText(token.toString())) {
            throw new IllegalStateException("飞书接口未返回 tenant_access_token");
        }

        long expireSeconds = toLong(response.get("expire"), 7200L);
        cachedTenantAccessToken = token.toString();
        tokenExpiresAt = Instant.now().plusSeconds(expireSeconds);
        return cachedTenantAccessToken;
    }

    private void validateConfig() {
        if (!properties.isEnabled()) {
            throw new IllegalStateException("飞书同步未启用，请配置 FEISHU_SHEET_ENABLED=true");
        }
        if (!StringUtils.hasText(properties.getAppId())
                || !StringUtils.hasText(properties.getAppSecret())
                || !StringUtils.hasText(properties.getSpreadsheetToken())) {
            throw new IllegalStateException("飞书同步缺少 appId/appSecret/spreadsheetToken 配置");
        }
    }

    private void assertFeishuSuccess(Map<?, ?> response, String message) {
        if (response == null) {
            throw new IllegalStateException(message + "：响应为空");
        }
        long code = toLong(response.get("code"), 0L);
        if (code != 0) {
            Object msg = response.get("msg");
            throw new IllegalStateException(message + "：" + (msg == null ? response : msg));
        }
    }

    private List<Object> row(Object... values) {
        List<Object> row = new ArrayList<>(values.length);
        for (Object value : values) {
            row.add(value == null ? "" : value);
        }
        return row;
    }

    private String statusText(Integer status) {
        if (status == null) {
            return "未知";
        }
        return switch (status) {
            case 0 -> "待接单";
            case 1 -> "进行中";
            case 2 -> "已完成";
            case 3 -> "已封禁";
            default -> "未知";
        };
    }

    private String formatDate(java.util.Date date) {
        if (date == null) {
            return "";
        }
        return DATE_TIME_FORMATTER.format(date.toInstant().atZone(ZoneId.of(properties.getZone())).toLocalDateTime());
    }

    private String formatDate(LocalDateTime dateTime) {
        if (dateTime == null) {
            return "";
        }
        return DATE_TIME_FORMATTER.format(dateTime);
    }

    private long toLong(Object value, long defaultValue) {
        if (value instanceof Number number) {
            return number.longValue();
        }
        if (value != null) {
            try {
                return Long.parseLong(value.toString());
            } catch (NumberFormatException ignored) {
                return defaultValue;
            }
        }
        return defaultValue;
    }

    public record SyncReport(String reportDate, int orderRows, int userRows) {
    }
}
