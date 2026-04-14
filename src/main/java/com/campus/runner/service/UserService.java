package com.campus.runner.service;

import com.campus.runner.entity.User;
import com.campus.runner.mapper.UserMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;
import java.util.List;

@Service
public class UserService {

    @Autowired
    private UserMapper userMapper;

    private final BCryptPasswordEncoder passwordEncoder = new BCryptPasswordEncoder();

    public User getUserById(Long id) {
        return userMapper.getUserById(id);
    }

    // 登录
    public User login(String username, String password) {
        User user = userMapper.getUserByUsername(username);
        if (user == null) {
            return null;
        }
        // 检查用户是否被封禁
        if ("BANNED".equals(user.getRole())) {
            return null;
        }
        // 兼容明文密码和BCrypt加密密码
        if (user.getPassword().startsWith("$2a$") || user.getPassword().startsWith("$2b$") || user.getPassword().startsWith("$2y$")) {
            // 是BCrypt加密的密码
            if (passwordEncoder.matches(password, user.getPassword())) {
                user.setPassword(null); // 不返回密码
                return user;
            }
        } else {
            // 是明文密码
            if (password.equals(user.getPassword())) {
                user.setPassword(null); // 不返回密码
                return user;
            }
        }
        return null;
    }

    // 注册
    public boolean register(User user) {
        User exist = userMapper.getUserByUsername(user.getUsername());
        if (exist != null) {
            return false;
        }
        user.setPassword(passwordEncoder.encode(user.getPassword()));
        // 如果前端传了ADMIN角色就使用，否则默认USER
        if (!"ADMIN".equals(user.getRole())) {
            user.setRole("USER");
        }
        return userMapper.insert(user) > 0;
    }

    // 测试方法：获取用户信息（包括密码）
    public User testUser(String username) {
        return userMapper.getUserByUsername(username);
    }

    // 获取所有用户
    public List<User> getAllUsers() {
        return userMapper.selectAllUsers();
    }

    // 更新用户角色
    public boolean updateUserRole(Long userId, String role) {
        return userMapper.updateById(userId, role) > 0;
    }

    // 更新用户状态
    public boolean updateUserStatus(Long userId, Integer status) {
        return userMapper.updateUserStatus(userId, status) > 0;
    }
}
