package com.campus.runner.controller;

import com.campus.runner.common.Result;
import com.campus.runner.entity.Comment;
import com.campus.runner.entity.Order;
import com.campus.runner.mapper.CommentMapper;
import com.campus.runner.mapper.OrderMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

@CrossOrigin
@RestController
@RequestMapping("/comment")
public class CommentController {

    @Autowired
    private CommentMapper commentMapper;

    @Autowired
    private OrderMapper orderMapper;

    @PostMapping("/add")
    public Result<Comment> addComment(@RequestBody Comment comment) {
        Result<?> validation = validateComment(comment);
        if (validation.getCode() != 200) {
            return Result.error(validation.getCode(), validation.getMsg());
        }

        Order order = orderMapper.getOrderById(comment.getOrderId());
        Long revieweeId = comment.getReviewerId().equals(order.getUserId())
                ? order.getRunnerId()
                : order.getUserId();

        comment.setTaskId(order.getTaskId());
        comment.setRevieweeId(revieweeId);
        comment.setContent(comment.getContent() == null ? "" : comment.getContent().trim());
        comment.setTags(comment.getTags() == null ? "" : comment.getTags().trim());

        int rows = commentMapper.insert(comment);
        if (rows <= 0) {
            return Result.fail("评价失败");
        }

        List<Comment> comments = commentMapper.selectByOrderId(comment.getOrderId());
        Comment saved = comments.stream()
                .filter(item -> item.getId().equals(comment.getId()))
                .findFirst()
                .orElse(comment);
        return Result.success("评价成功", saved);
    }

    @GetMapping("/order/{orderId}")
    public Result<List<Comment>> getByOrder(@PathVariable Long orderId) {
        return Result.success(commentMapper.selectByOrderId(orderId));
    }

    @GetMapping("/list/{taskId}")
    public Result<List<Comment>> getByTask(@PathVariable Long taskId) {
        return Result.success(commentMapper.selectByTaskId(taskId));
    }

    @GetMapping("/mine")
    public Result<List<Comment>> getMine(@RequestParam Long userId) {
        return Result.success(commentMapper.selectByReviewerId(userId));
    }

    @GetMapping("/received")
    public Result<List<Comment>> getReceived(@RequestParam Long userId) {
        return Result.success(commentMapper.selectByRevieweeId(userId));
    }

    @GetMapping("/summary")
    public Result<Map<String, Object>> getSummary(@RequestParam Long userId) {
        Map<String, Object> summary = new HashMap<>();
        Double averageScore = commentMapper.averageScoreByRevieweeId(userId);
        int count = commentMapper.countByRevieweeId(userId);
        summary.put("averageScore", averageScore == null ? 0 : Math.round(averageScore * 10.0) / 10.0);
        summary.put("count", count);
        return Result.success(summary);
    }

    @GetMapping("/list")
    public Result<List<Comment>> getAllComments() {
        return Result.success(commentMapper.selectAll());
    }

    @DeleteMapping
    public Result<?> delete(@RequestParam Long commentId) {
        int rows = commentMapper.deleteById(commentId);
        return rows > 0 ? Result.success("删除成功") : Result.fail("评价不存在");
    }

    private Result<?> validateComment(Comment comment) {
        if (comment.getOrderId() == null) {
            return Result.error(400, "orderId 不能为空");
        }
        if (comment.getReviewerId() == null) {
            return Result.error(400, "reviewerId 不能为空");
        }
        if (comment.getScore() == null || comment.getScore() < 1 || comment.getScore() > 5) {
            return Result.error(400, "score 必须在 1 到 5 之间");
        }
        if (comment.getContent() == null || comment.getContent().trim().isEmpty()) {
            return Result.error(400, "评价内容不能为空");
        }
        if (comment.getContent().trim().length() > 200) {
            return Result.error(400, "评价内容不能超过 200 字");
        }

        Order order = orderMapper.getOrderById(comment.getOrderId());
        if (order == null) {
            return Result.fail("订单不存在");
        }
        if (order.getStatus() == null || order.getStatus() != 2) {
            return Result.fail("订单完成后才能评价");
        }
        if (order.getRunnerId() == null) {
            return Result.fail("订单没有接单人，无法评价");
        }
        boolean isPublisher = comment.getReviewerId().equals(order.getUserId());
        boolean isRunner = comment.getReviewerId().equals(order.getRunnerId());
        if (!isPublisher && !isRunner) {
            return Result.error(403, "只能评价自己参与的订单");
        }
        if (commentMapper.countByOrderAndReviewer(comment.getOrderId(), comment.getReviewerId()) > 0) {
            return Result.fail("你已经评价过这个订单");
        }

        return Result.success("校验通过");
    }
}
