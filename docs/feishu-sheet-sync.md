# 飞书表格同步

后端支持把每天的订单和人员信息同步到飞书普通表格。同步逻辑放在 Spring Boot 后端，不需要改小程序前端。

## 同步内容

订单日报建议表头：

| report_date | order_id | task_id | title | description | reward | status | status_text | publisher_id | publisher_name | publisher_phone | runner_id | runner_name | runner_phone | create_time |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

人员信息建议表头：

| report_date | user_id | username | phone | role | status | create_time |
| --- | --- | --- | --- | --- | --- | --- |

## 飞书配置

1. 在飞书开放平台创建企业自建应用。
2. 给应用开通云文档/电子表格读写权限，并发布应用版本。
3. 创建一个飞书普通表格，把应用加入文档协作者。
4. 从表格 URL 中取得 `spreadsheet_token`，从 `sheet=` 参数或表格信息中取得 `sheet_id`。
5. 设置后端环境变量：

```bash
FEISHU_SHEET_ENABLED=true
FEISHU_APP_ID=cli_xxx
FEISHU_APP_SECRET=xxx
FEISHU_SPREADSHEET_TOKEN=shtxxx
FEISHU_ORDER_RANGE=订单表sheetId!A:O
FEISHU_USER_RANGE=人员表sheetId!A:G
FEISHU_SYNC_CRON='0 5 0 * * ?'
FEISHU_SYNC_ZONE=Asia/Shanghai
```

`FEISHU_SYNC_CRON='0 5 0 * * ?'` 表示每天 00:05 同步前一天数据。

## 手动测试

后端启动后可以手动触发同步当天数据：

```bash
curl -X POST "http://localhost:8080/admin/feishu/sync?date=2026-04-22"
```

如果没有传 `date`，默认同步当天数据。定时任务自动同步的是前一天数据。
