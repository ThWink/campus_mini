package com.campus.runner.entity;

import lombok.Data;
import java.util.Date;

@Data
public class Order {
    private Long id;
    private Long userId;
    private Long taskId;
    private Long runnerId;
    private Integer status;
    private Date createTime;

    // --- 业务与联表字段 ---
    private Long publisherId; // 逻辑字段：对应发布任务的人
    private String title;
    private String description;
    private Double reward;
}