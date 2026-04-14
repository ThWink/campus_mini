package com.campus.runner.entity;

import java.time.LocalDateTime;

public class User {

    private Long id;
    private String username;
    private String password;
    private String phone;
    private String role;
    private Integer status;
    private LocalDateTime createTime;

    public User() {
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public String getUsername() {
        return username;
    }   // ← 之前报错就是因为你没这个

    public void setUsername(String username) {
        this.username = username;
    }

    public String getPassword() {
        return password;
    }   // ← 登录必须用

    public void setPassword(String password) {
        this.password = password;
    }

    public String getPhone() {
        return phone;
    }

    public void setPhone(String phone) {
        this.phone = phone;
    }

    public String getRole() {
        return role;
    }

    public void setRole(String role) {
        this.role = role;
    }

    public Integer getStatus() {
        return status;
    }

    public void setStatus(Integer status) {
        this.status = status;
    }

    public LocalDateTime getCreateTime() {
        return createTime;
    }

    public void setCreateTime(LocalDateTime createTime) {
        this.createTime = createTime;
    }
}
