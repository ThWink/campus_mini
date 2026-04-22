package com.campus.runner.controller;

import com.campus.runner.common.Result;
import com.campus.runner.entity.Order;
import com.campus.runner.mapper.OrderMapper;
import com.campus.runner.service.TaskService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@CrossOrigin
@RestController
@RequestMapping("/api/internal")
public class InternalAiController {

    @Autowired
    private OrderMapper orderMapper;

    @Autowired
    private TaskService taskService;

    @GetMapping("/order/status")
    public Result<Order> getOrderStatus(
            @RequestParam("id") Long orderId,
            @RequestParam(value = "userId", required = false) Long userId) {
        if (orderId == null) {
            return Result.error(400, "id 不能为空");
        }

        Order order = orderMapper.getOrderById(orderId);
        if (order == null) {
            return Result.fail("订单不存在");
        }

        if (userId != null && !userId.equals(order.getUserId()) && !userId.equals(order.getRunnerId())) {
            return Result.error(403, "只能查询自己的订单");
        }

        return Result.success(order);
    }

    @GetMapping("/order/published")
    public Result<List<Order>> getPublishedOrders(@RequestParam("userId") Long userId) {
        if (userId == null) {
            return Result.error(400, "userId 不能为空");
        }
        return Result.success(orderMapper.selectByUserId(userId));
    }

    @GetMapping("/order/accepted")
    public Result<List<Order>> getAcceptedOrders(@RequestParam("userId") Long userId) {
        if (userId == null) {
            return Result.error(400, "userId 不能为空");
        }
        return Result.success(orderMapper.selectByRunnerId(userId));
    }

    @GetMapping("/order/mine")
    public Result<Map<String, List<Order>>> getMyOrders(@RequestParam("userId") Long userId) {
        if (userId == null) {
            return Result.error(400, "userId 不能为空");
        }

        Map<String, List<Order>> result = new HashMap<>();
        result.put("published", orderMapper.selectByUserId(userId));
        result.put("accepted", orderMapper.selectByRunnerId(userId));
        return Result.success(result);
    }

    @PostMapping("/task/publish")
    public Result<Order> publishTask(@RequestBody Map<String, Object> params) {
        Long userId = toLong(params.get("userId"));
        String title = toStringValue(params.get("title"));
        String description = toStringValue(params.get("description"));
        Double reward = toDouble(params.get("reward"));
        return taskService.publishForAgent(userId, title, description, reward);
    }

    private Long toLong(Object value) {
        if (value == null) {
            return null;
        }
        if (value instanceof Number) {
            return ((Number) value).longValue();
        }
        try {
            return Long.parseLong(String.valueOf(value));
        } catch (NumberFormatException e) {
            return null;
        }
    }

    private Double toDouble(Object value) {
        if (value == null) {
            return null;
        }
        if (value instanceof Number) {
            return ((Number) value).doubleValue();
        }
        try {
            return new BigDecimal(String.valueOf(value).replace("元", "").replace("块", "")).doubleValue();
        } catch (NumberFormatException e) {
            return null;
        }
    }

    private String toStringValue(Object value) {
        return value == null ? null : String.valueOf(value);
    }
}
