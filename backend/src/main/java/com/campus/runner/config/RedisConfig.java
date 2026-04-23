package com.campus.runner.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.redis.connection.RedisConnectionFactory;
import org.springframework.data.redis.connection.RedisPassword;
import org.springframework.data.redis.connection.RedisStandaloneConfiguration;
import org.springframework.data.redis.connection.lettuce.LettuceConnectionFactory;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.util.StringUtils;

@Configuration
public class RedisConfig {

    @Bean
    public RedisConnectionFactory redisConnectionFactory(
            @Value("${REDIS_HOST:127.0.0.1}") String host,
            @Value("${REDIS_PORT:6379}") int port,
            @Value("${REDIS_DB:0}") int database,
            @Value("${REDIS_PASSWORD:}") String password,
            @Value("${REDIS_AUTH_ENABLED:false}") boolean authEnabled) {
        RedisStandaloneConfiguration config = new RedisStandaloneConfiguration(host, port);
        config.setDatabase(database);

        if (authEnabled && StringUtils.hasText(password)) {
            config.setPassword(RedisPassword.of(password));
        }

        return new LettuceConnectionFactory(config);
    }

    @Bean
    public StringRedisTemplate stringRedisTemplate(RedisConnectionFactory redisConnectionFactory) {
        return new StringRedisTemplate(redisConnectionFactory);
    }
}
