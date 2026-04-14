package com.campus.runner.controller;

import com.campus.runner.common.Result;
import com.campus.runner.entity.Order;
import com.campus.runner.mapper.OrderMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

@CrossOrigin
@RestController
@RequestMapping("/api/internal")
public class InternalAiController {

    @Autowired
    private OrderMapper orderMapper;

    @GetMapping("/order/status")
    public Result<Order> getOrderStatus(@RequestParam("id") Long orderId) {
        if (orderId == null) {
            return Result.error(400, "id不能为空");
        }
        Order order = orderMapper.getOrderById(orderId);
        if (order == null) {
            return Result.fail("订单不存在");
        }
        return Result.success(order);
    }
}
