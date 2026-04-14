package com.campus.runner;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
@MapperScan("com.campus.runner.mapper")
public class CampusRunnerApplication {
	public static void main(String[] args) {
		SpringApplication.run(CampusRunnerApplication.class, args);
	}
}