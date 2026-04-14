package com.campus.runner.mapper;

import com.campus.runner.entity.User;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface UserMapper {

    User getUserById(@Param("id") Long id);

    User getUserByUsername(@Param("username") String username);

    List<User> selectAllUsers();

    int updateById(@Param("id") Long id, @Param("role") String role);

    int updateUserStatus(@Param("id") Long id, @Param("status") Integer status);

    int insert(User user);
}
