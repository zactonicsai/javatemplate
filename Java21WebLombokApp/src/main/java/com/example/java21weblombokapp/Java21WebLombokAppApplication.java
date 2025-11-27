package com.example.java21weblombokapp;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Import;

import com.example.demo.config.CorsConfig;
import com.example.demo.config.SecurityConfig;

@SpringBootApplication
@Import({SecurityConfig.class, CorsConfig.class})
public class Java21WebLombokAppApplication {

	public static void main(String[] args) {
		SpringApplication.run(Java21WebLombokAppApplication.class, args);
	}

}
