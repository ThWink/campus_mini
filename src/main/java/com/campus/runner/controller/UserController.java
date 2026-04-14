package com.campus.runner.controller;

import com.campus.runner.common.Result;
import com.campus.runner.entity.User;
import com.campus.runner.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@CrossOrigin
@RestController
@RequestMapping("/user")
public class UserController {

    @Autowired
    private UserService userService;

    @PostMapping("/login")
    public Result<User> login(@RequestBody User user) {
        String username = user.getUsername();
        String password = user.getPassword();

        User u = userService.login(username, password);
        if (u != null) {
            return Result.success(u);
        }
        return Result.fail("用户名或密码错误");
    }

    @PostMapping("/register")
    public Result<?> register(@RequestBody User user) {
        boolean success = userService.register(user);
        if (success) {
            return Result.success("注册成功");
        } else {
            return Result.fail("用户名已存在");
        }
    }
}
