package com.campus.runner.mapper;

import com.campus.runner.entity.Comment;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;
import java.util.List;

@Mapper
public interface CommentMapper {
    int insert(Comment comment);
    List<Comment> selectByTaskId(@Param("taskId") Long taskId);
    List<Comment> selectAll();
}