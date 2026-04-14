package com.campus.runner.service;

import com.alibaba.fastjson.JSON;
import com.campus.runner.common.Result;
import com.campus.runner.entity.Order;
import com.campus.runner.mapper.OrderMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import java.util.List;
import java.util.Objects;
import java.util.concurrent.TimeUnit;

@Service
public class OrderService {

    @Autowired
    private OrderMapper orderMapper;

    @Autowired
    private StringRedisTemplate redisTemplate;

    /**
     * 抢单逻辑：加入 Redis 分布式锁
     */
    @Transactional
    public Result acceptOrder(Long orderId, Long runnerId) {
        // 1. Redis 分布式锁，防止多人同时操作同一个订单
        String lockKey = "lock:order:" + orderId;
        // setIfAbsent 等同于 SETNX，如果 Key 不存在则设置成功并返回 true
        Boolean isLock = redisTemplate.opsForValue().setIfAbsent(lockKey, "1", 5, TimeUnit.SECONDS);

        if (Boolean.FALSE.equals(isLock)) {
            return Result.error(400, "系统繁忙，请稍后再试");
        }

        try {
            Order order = orderMapper.getOrderById(orderId);
            if (order == null) return Result.error(400, "订单不存在");

            // 状态校验
            if (order.getStatus() != 0) return Result.error(400, "订单已被抢走或已失效");

            // 🔴 拦截逻辑：禁止自发自抢
            if (Objects.equals(order.getUserId(), runnerId)) {
                return Result.error(400, "你不能抢自己发布的订单");
            }

            // 2. 更新 MySQL 状态为 1 (配送中)
            int rows = orderMapper.updateStatus(orderId, 1, runnerId);
            if (rows > 0) {
                // 3. 抢单成功，清除大厅列表的 Redis 缓存（强制下次查询走数据库）
                redisTemplate.delete("order:pending:list");
                return Result.success("抢单成功，请尽快送达");
            }
            return Result.error(500, "服务器繁忙，抢单失败");
        } finally {
            // 4. 释放锁
            redisTemplate.delete(lockKey);
        }
    }

    /**
     * 确认完成逻辑
     */
    @Transactional
    public Result completeOrder(Long orderId) {
        Order order = orderMapper.getOrderById(orderId);

        if (order == null) return Result.error(404, "未找到该订单");
        if (order.getStatus() != 1) return Result.error(400, "当前状态不是配送中，无法完成");

        // 更新状态为 2 (已完成)
        int rows = orderMapper.updateStatus(orderId, 2, null);
        return rows > 0 ? Result.success("订单已完成") : Result.error(500, "操作失败");
    }

    public List<Order> getMyPublished(Long userId) {
        return orderMapper.selectByUserId(userId);
    }

    public List<Order> getMyTasks(Long runnerId) {
        return orderMapper.selectByRunnerId(runnerId);
    }

    public List<Order> getAllOrders() {
        return orderMapper.selectAllOrders();
    }

    public int updateOrderStatus(Long orderId, Integer status) {
        return orderMapper.updateOrderStatus(orderId, status);
    }
}