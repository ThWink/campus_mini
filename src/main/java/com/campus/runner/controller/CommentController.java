package com.campus.runner.controller;

import com.campus.runner.common.Result;
import com.campus.runner.entity.Comment;
import com.campus.runner.mapper.CommentMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@CrossOrigin
@RestController
@RequestMapping("/comment")
public class CommentController {

    @Autowired
    private CommentMapper commentMapper;

    @PostMapping("/add")
    public Result<?> addComment(@RequestBody Comment comment) {
        if (comment.getTaskId() == null || comment.getScore() == null) {
            return Result.error(400, "taskId和score不能为空");
        }
        int rows = commentMapper.insert(comment);
        if (rows > 0) {
            return Result.success("评价成功");
        } else {
            return Result.fail("评价失败");
        }
    }

    @GetMapping("/list/{taskId}")
    public Result<List<Comment>> getComments(@PathVariable Long taskId) {
        List<Comment> comments = commentMapper.selectByTaskId(taskId);
        return Result.success(comments);
    }

    @GetMapping("/list")
    public Result<List<Comment>> getAllComments() {
        List<Comment> comments = commentMapper.selectAll();
        return Result.success(comments);
    }
}