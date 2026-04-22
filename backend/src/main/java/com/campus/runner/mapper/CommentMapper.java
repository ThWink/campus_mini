package com.campus.runner.mapper;

import com.campus.runner.entity.Comment;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface CommentMapper {
    int insert(Comment comment);

    int deleteById(@Param("id") Long id);

    int countByOrderAndReviewer(@Param("orderId") Long orderId, @Param("reviewerId") Long reviewerId);

    List<Comment> selectByOrderId(@Param("orderId") Long orderId);

    List<Comment> selectByTaskId(@Param("taskId") Long taskId);

    List<Comment> selectByReviewerId(@Param("reviewerId") Long reviewerId);

    List<Comment> selectByRevieweeId(@Param("revieweeId") Long revieweeId);

    List<Comment> selectAll();

    Double averageScoreByRevieweeId(@Param("revieweeId") Long revieweeId);

    int countByRevieweeId(@Param("revieweeId") Long revieweeId);
}
