package com.campus.runner.entity;

import lombok.Data;
import java.util.Date;

@Data
public class Task {
    private Long id;
    private Long publisherId;   // 发布者ID
    private String title;       // 标题
    private String description; // 描述
    private Double reward;      // 赏金
    private Integer status;     // 0-待接单, 1-已接单, 2-已完成
    private Date createTime;
}