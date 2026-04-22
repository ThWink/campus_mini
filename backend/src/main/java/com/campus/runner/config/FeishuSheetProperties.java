package com.campus.runner.config;

import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

@Component
@ConfigurationProperties(prefix = "feishu.sheet")
public class FeishuSheetProperties {

    private boolean enabled = false;
    private String baseUrl = "https://open.feishu.cn";
    private String appId;
    private String appSecret;
    private String spreadsheetToken;
    private String orderRange = "Sheet1!A:O";
    private String userRange = "Sheet1!A:G";
    private String cron = "0 5 0 * * ?";
    private String zone = "Asia/Shanghai";
    private boolean syncOrders = true;
    private boolean syncUsers = true;

    public boolean isEnabled() {
        return enabled;
    }

    public void setEnabled(boolean enabled) {
        this.enabled = enabled;
    }

    public String getBaseUrl() {
        return baseUrl;
    }

    public void setBaseUrl(String baseUrl) {
        this.baseUrl = baseUrl;
    }

    public String getAppId() {
        return appId;
    }

    public void setAppId(String appId) {
        this.appId = appId;
    }

    public String getAppSecret() {
        return appSecret;
    }

    public void setAppSecret(String appSecret) {
        this.appSecret = appSecret;
    }

    public String getSpreadsheetToken() {
        return spreadsheetToken;
    }

    public void setSpreadsheetToken(String spreadsheetToken) {
        this.spreadsheetToken = spreadsheetToken;
    }

    public String getOrderRange() {
        return orderRange;
    }

    public void setOrderRange(String orderRange) {
        this.orderRange = orderRange;
    }

    public String getUserRange() {
        return userRange;
    }

    public void setUserRange(String userRange) {
        this.userRange = userRange;
    }

    public String getCron() {
        return cron;
    }

    public void setCron(String cron) {
        this.cron = cron;
    }

    public String getZone() {
        return zone;
    }

    public void setZone(String zone) {
        this.zone = zone;
    }

    public boolean isSyncOrders() {
        return syncOrders;
    }

    public void setSyncOrders(boolean syncOrders) {
        this.syncOrders = syncOrders;
    }

    public boolean isSyncUsers() {
        return syncUsers;
    }

    public void setSyncUsers(boolean syncUsers) {
        this.syncUsers = syncUsers;
    }
}
