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
        task.setStatus(0); // 设置任务为待接单
        int rows = taskMapper.insert(task);

        if (rows > 0) {
            Order order = new Order();
            // 这里把任务的发布者 ID 赋给 order 的 userId
            order.setUserId(task.getPublisherId());
            order.setTaskId(task.getId());
            order.setStatus(0);

            // 关键：这里可以调用 setPublisherId 存内存，但 Mapper 映射时不要去存数据库
            order.setPublisherId(task.getPublisherId());

            orderMapper.insert(order);
            return Result.success("发布成功");
        }
        return Result.fail("发布失败");
    }
}