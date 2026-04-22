package com.campus.runner.service;

import com.campus.runner.common.Result;
import com.campus.runner.entity.Order;
import com.campus.runner.entity.Task;
import com.campus.runner.mapper.OrderMapper;
import com.campus.runner.mapper.TaskMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class TaskService {

    @Autowired
    private TaskMapper taskMapper;

    @Autowired
    private OrderMapper orderMapper;

    @Transactional(rollbackFor = Exception.class)
    public Result save(Task task) {
        Result<Order> result = createTaskAndOrder(task);
        if (result.getCode() == 200) {
            return Result.success("发布成功");
        }
        return Result.fail(result.getMsg());
    }

    @Transactional(rollbackFor = Exception.class)
    public Result<Order> publishForAgent(Long publisherId, String title, String description, Double reward) {
        if (publisherId == null) {
            return Result.error(400, "publisherId 不能为空");
        }
        if (title == null || title.trim().isEmpty()) {
            return Result.error(400, "title 不能为空");
        }
        if (reward == null || reward < 0) {
            return Result.error(400, "reward 不能小于 0");
        }

        Task task = new Task();
        task.setPublisherId(publisherId);
        task.setTitle(title.trim());
        task.setDescription(description == null || description.trim().isEmpty() ? title.trim() : description.trim());
        task.setReward(reward);
        return createTaskAndOrder(task);
    }

    private Result<Order> createTaskAndOrder(Task task) {
        task.setStatus(0);
        int rows = taskMapper.insert(task);

        if (rows <= 0) {
            return Result.fail("发布失败");
        }

        Order order = new Order();
        order.setUserId(task.getPublisherId());
        order.setTaskId(task.getId());
        order.setStatus(0);
        order.setPublisherId(task.getPublisherId());

        orderMapper.insert(order);
        return Result.success("发布成功", orderMapper.getOrderById(order.getId()));
    }
}
