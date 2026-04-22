package com.campus.runner.entity;

import lombok.Data;

import java.util.Date;

@Data
public class Comment {
    private Long id;
    private Long orderId;
    private Long taskId;
    private Long reviewerId;
    private Long revieweeId;
    private Integer score;
    private String content;
    private String tags;
    private Date createTime;

    private String orderTitle;
    private String reviewerName;
    private String revieweeName;
}
