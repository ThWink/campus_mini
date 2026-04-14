package com.campus.runner.controller;

import com.campus.runner.common.Result;
import com.campus.runner.entity.Task;
import com.campus.runner.service.TaskService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/task")
public class TaskController {

    @Autowired
    private TaskService taskService;

    /**
     * 发布任务接口
     * POST http://localhost:8080/task/save
     */
    @PostMapping("/save")
    public Result save(@RequestBody Task task) {
        return taskService.save(task);
    }
}