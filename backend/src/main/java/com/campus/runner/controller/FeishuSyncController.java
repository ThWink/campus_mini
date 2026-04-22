package com.campus.runner.controller;

import com.campus.runner.common.Result;
import com.campus.runner.service.FeishuSheetSyncService;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.time.LocalDate;

@RestController
@RequestMapping("/admin/feishu")
public class FeishuSyncController {

    private final FeishuSheetSyncService feishuSheetSyncService;

    public FeishuSyncController(FeishuSheetSyncService feishuSheetSyncService) {
        this.feishuSheetSyncService = feishuSheetSyncService;
    }

    @PostMapping("/sync")
    public Result<FeishuSheetSyncService.SyncReport> sync(
            @RequestParam(required = false)
            @DateTimeFormat(iso = DateTimeFormat.ISO.DATE)
            LocalDate date) {
        try {
            LocalDate reportDate = date == null ? LocalDate.now() : date;
            return Result.success("飞书同步完成", feishuSheetSyncService.syncDate(reportDate));
        } catch (IllegalStateException e) {
            return Result.error(400, e.getMessage());
        } catch (Exception e) {
            return Result.error(500, e.getMessage());
        }
    }
}
