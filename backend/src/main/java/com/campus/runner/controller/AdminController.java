package com.campus.runner.controller;

import com.campus.runner.common.Result;
import com.campus.runner.entity.Comment;
import com.campus.runner.entity.Order;
import com.campus.runner.entity.User;
import com.campus.runner.mapper.CommentMapper;
import com.campus.runner.service.OrderService;
import com.campus.runner.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@CrossOrigin
@RestController
@RequestMapping("/admin")
public class AdminController {

    @Autowired
    private UserService userService;

    @Autowired
    private OrderService orderService;

    @Autowired
    private CommentMapper commentMapper;

    // 内存存储模拟订单数据
    private static List<Order> orders = new ArrayList<>();
    private static long orderCounter = 1;

    // 初始化订单数据
    static {
        // 添加测试订单
        Order order1 = new Order();
        order1.setId(orderCounter++);
        order1.setUserId(1L);
        order1.setTaskId(1L);
        order1.setTitle("取快递");
        order1.setReward(5.00);
        order1.setStatus(0);
        orders.add(order1);

        Order order2 = new Order();
        order2.setId(orderCounter++);
        order2.setUserId(1L);
        order2.setTaskId(2L);
        order2.setTitle("买饭");
        order2.setReward(8.00);
        order2.setStatus(1);
        orders.add(order2);

        Order order3 = new Order();
        order3.setId(orderCounter++);
        order3.setUserId(2L);
        order3.setTaskId(3L);
        order3.setTitle("打印资料");
        order3.setReward(3.00);
        order3.setStatus(2);
        orders.add(order3);
    }

    @GetMapping("/users")
    public Result<List<User>> listUsers() {
        try {
            List<User> users = userService.getAllUsers();
            // 移除密码字段，处理null值
            List<User> usersWithoutPassword = users.stream()
                    .map(user -> {
                        User u = new User();
                        u.setId(user.getId());
                        u.setUsername(user.getUsername());
                        u.setPhone(user.getPhone());
                        u.setRole(user.getRole());
                        u.setStatus(user.getStatus() != null ? user.getStatus() : 1);
                        u.setCreateTime(user.getCreateTime());
                        return u;
                    })
                    .collect(Collectors.toList());
            return Result.success(usersWithoutPassword);
        } catch (Exception e) {
            e.printStackTrace();
            return Result.error(500, "获取用户列表失败: " + e.getMessage());
        }
    }

    @GetMapping("/orders")
    public Result<List<Order>> listOrders() {
        try {
            List<Order> orders = orderService.getAllOrders();
            return Result.success(orders);
        } catch (Exception e) {
            e.printStackTrace();
            return Result.error(500, "获取订单列表失败: " + e.getMessage());
        }
    }

    @PostMapping("/updateUserRole")
    public Result<?> updateUserRole(@RequestBody Map<String, Object> params) {
        Long userId = toLong(params.get("userId"));
        String role = params.get("role") == null ? null : params.get("role").toString();
        if (userId == null || role == null) {
            return Result.error(400, "userId 和 role 不能为空");
        }
        boolean success = userService.updateUserRole(userId, role);
        return success ? Result.success("更新成功") : Result.fail("用户不存在");
    }

    @PostMapping("/updateOrderStatus")
    public Result<?> updateOrderStatus(@RequestBody Map<String, Object> params) {
        Long orderId = toLong(params.get("orderId"));
        Integer status = toInteger(params.get("status"));
        if (orderId == null || status == null) {
            return Result.error(400, "orderId 和 status 不能为空");
        }
        int rows = orderService.updateOrderStatus(orderId, status);
        if (rows > 0) {
            return Result.success("更新成功");
        } else {
            return Result.fail("订单不存在");
        }
    }

    @PostMapping("/banUser")
    public Result<?> banUser(@RequestBody BanUserRequest request) {
        if (request.getUserId() == null) {
            return Result.error(400, "userId 不能为空");
        }
        boolean success = userService.updateUserRole(request.getUserId(), "BANNED");
        if (success) {
            return Result.success("用户已封禁");
        } else {
            return Result.fail("用户不存在");
        }
    }

    @PostMapping("/unbanUser")
    public Result<?> unbanUser(@RequestBody BanUserRequest request) {
        if (request.getUserId() == null) {
            return Result.error(400, "userId 不能为空");
        }
        boolean success = userService.updateUserRole(request.getUserId(), "USER");
        if (success) {
            return Result.success("用户已解封");
        } else {
            return Result.fail("用户不存在");
        }
    }

    @PostMapping("/banOrder")
    public Result<?> banOrder(@RequestBody BanOrderRequest request) {
        if (request.getOrderId() == null) {
            return Result.error(400, "orderId 不能为空");
        }
        try {
            int result = orderService.updateOrderStatus(request.getOrderId(), 3);
            if (result > 0) {
                return Result.success("订单已封禁");
            } else {
                return Result.fail("订单不存在");
            }
        } catch (Exception e) {
            e.printStackTrace();
            return Result.error(500, "封禁订单失败: " + e.getMessage());
        }
    }

    // 用于接收banUser和unbanUser请求的参数
    private static class BanUserRequest {
        private Long userId;

        public Long getUserId() {
            return userId;
        }

        public void setUserId(Long userId) {
            this.userId = userId;
        }
    }

    // 用于接收banOrder请求的参数
    private static class BanOrderRequest {
        private Long orderId;

        public Long getOrderId() {
            return orderId;
        }

        public void setOrderId(Long orderId) {
            this.orderId = orderId;
        }
    }

    @GetMapping("/comments")
    public Result<List<Comment>> listComments() {
        try {
            return Result.success(commentMapper.selectAll());
        } catch (Exception e) {
            e.printStackTrace();
            return Result.error(500, "获取评价列表失败: " + e.getMessage());
        }
    }

    @DeleteMapping("/comments")
    public Result<?> deleteComment(@RequestParam Long commentId) {
        if (commentId == null) {
            return Result.error(400, "commentId 不能为空");
        }
        int rows = commentMapper.deleteById(commentId);
        return rows > 0 ? Result.success("删除成功") : Result.fail("评价不存在");
    }

    private Long toLong(Object value) {
        if (value == null) {
            return null;
        }
        if (value instanceof Number number) {
            return number.longValue();
        }
        try {
            return Long.parseLong(value.toString());
        } catch (NumberFormatException e) {
            return null;
        }
    }

    private Integer toInteger(Object value) {
        if (value == null) {
            return null;
        }
        if (value instanceof Number number) {
            return number.intValue();
        }
        try {
            return Integer.parseInt(value.toString());
        } catch (NumberFormatException e) {
            return null;
        }
    }
}
