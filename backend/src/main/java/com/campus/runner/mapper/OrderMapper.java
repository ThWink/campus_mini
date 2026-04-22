package com.campus.runner.mapper;

import com.campus.runner.entity.Order;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import java.time.LocalDateTime;
import java.util.List;

@Mapper
public interface OrderMapper {
    // 基础操作
    int insert(Order order);
    Order getOrderById(@Param("id") Long id);

    // 管理员：获取所有订单
    List<Order> selectAllOrders();

    // 1. 获取大厅待接单列表 (status = 0)
    List<Order> selectPendingOrders();

    // 2. 更新订单状态（用于接单和完成任务）
    int updateStatus(@Param("id") Long id, @Param("status") Integer status, @Param("runnerId") Long runnerId);

    // 3. 🔴 新增：获取我发布的订单（根据发布者 user_id 查询）
    List<Order> selectByUserId(@Param("userId") Long userId);

    // 4. 🔴 新增：获取我接取的订单（根据接单人 runner_id 查询）
    List<Order> selectByRunnerId(@Param("runnerId") Long runnerId);

    // 5. 🔴 新增：管理员更新订单状态
    int updateOrderStatus(@Param("orderId") Long orderId, @Param("status") Integer status);

    List<Order> selectByCreateTimeRange(@Param("startTime") LocalDateTime startTime,
                                        @Param("endTime") LocalDateTime endTime);
}
