package com.example.app;

import com.example.demo.config.SecurityConfig;
import com.example.demo.config.CorsConfig;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Import;

/**
 * Example Spring Boot application using the keycloak-spring-security-lib
 */
@SpringBootApplication
@Import({SecurityConfig.class, CorsConfig.class})
public class ExampleApplication {
    
    public static void main(String[] args) {
        SpringApplication.run(ExampleApplication.class, args);
    }
}
