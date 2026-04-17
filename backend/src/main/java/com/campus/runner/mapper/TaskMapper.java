package com.campus.runner.mapper;

import com.campus.runner.entity.Task;
import org.apache.ibatis.annotations.Mapper;

@Mapper
public interface TaskMapper {
    /**
     * 插入任务，并回填自增主键 ID
     */
    int insert(Task task);
}