package com.campus.runner.controller;

import com.campus.runner.common.Result;
import com.campus.runner.entity.Order;
import com.campus.runner.service.OrderService;
import com.campus.runner.mapper.OrderMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/order")
public class OrderController {

    @Autowired
    private OrderService orderService;

    @Autowired
    private OrderMapper orderMapper;

    /**
     * 1. 获取所有待接单的任务（用于大厅展示）
     * GET http://localhost:8080/order/listPending
     */
    @GetMapping("/listPending")
    public Result<List<Order>> listPending() {
        List<Order> list = orderMapper.selectPendingOrders();
        return Result.success(list);
    }

    @GetMapping("/pending")
    public Result<List<Order>> pending() {
        return listPending();
    }

    /**
     * 2. 抢单接口
     * POST http://localhost:8080/order/accept
     * 请求体示例: {"orderId": 10, "runnerId": 13}
     */
    @PostMapping("/accept")
    public Result accept(@RequestBody Map<String, Long> params) {
        Long orderId = params.get("orderId");
        Long runnerId = params.get("runnerId");

        if (orderId == null || runnerId == null) {
            return Result.error(400, "订单ID或接单人ID不能为空");
        }

        // 调用 Service 层处理：修改订单状态为 1 (已接单)，写入 runnerId
        return orderService.acceptOrder(orderId, runnerId);
    }

    @PutMapping("/accept")
    public Result acceptByQuery(@RequestParam Long orderId, @RequestParam Long runnerId) {
        if (orderId == null || runnerId == null) {
            return Result.error(400, "订单ID或接单人ID不能为空");
        }
        return orderService.acceptOrder(orderId, runnerId);
    }

    /**
     * 3. 获取我发布的订单进度（发布人视角）
     * GET http://localhost:8080/order/myPublished?userId=13
     */
    @GetMapping("/myPublished")
    public Result<List<Order>> getMyPublished(@RequestParam Long userId) {
        // 在 OrderMapper 中实现：SELECT * FROM orders WHERE user_id = #{userId}
        List<Order> list = orderMapper.selectByUserId(userId);
        return Result.success(list);
    }

    /**
     * 4. 获取我接取的任务进度（接单人视角）
     * GET http://localhost:8080/order/myTasks?runnerId=13
     */
    @GetMapping("/myTasks")
    public Result<List<Order>> getMyTasks(@RequestParam Long runnerId) {
        // 在 OrderMapper 中实现：SELECT * FROM orders WHERE runner_id = #{runnerId}
        List<Order> list = orderMapper.selectByRunnerId(runnerId);
        return Result.success(list);
    }

    /**
     * 5. 确认送达/完成任务
     * POST http://localhost:8080/order/complete
     * 请求体示例: {"orderId": 10}
     */
    @PostMapping("/complete")
    public Result complete(@RequestBody Map<String, Long> params) {
        Long orderId = params.get("orderId");
        if (orderId == null) {
            return Result.error(400, "订单ID不能为空");
        }

        // 调用 Service 层处理：修改状态为 2 (已完成)
        return orderService.completeOrder(orderId);
    }
}
