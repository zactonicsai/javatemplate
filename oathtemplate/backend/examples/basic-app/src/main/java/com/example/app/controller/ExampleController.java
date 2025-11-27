package com.example.app.controller;

import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.GrantedAuthority;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.HashMap;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * Example controller demonstrating the use of the library's security features
 */
@RestController
@RequestMapping("/api")
public class ExampleController {
    
    @GetMapping("/hello")
    @PreAuthorize("hasRole('USER')")
    public Map<String, Object> hello(Authentication auth) {
        Map<String, Object> response = new HashMap<>();
        response.put("message", "Hello, " + auth.getName());
        response.put("roles", auth.getAuthorities().stream()
            .map(GrantedAuthority::getAuthority)
            .collect(Collectors.toList()));
        return response;
    }
    
    @GetMapping("/admin")
    @PreAuthorize("hasRole('ADMIN')")
    public Map<String, String> adminOnly() {
        Map<String, String> response = new HashMap<>();
        response.put("message", "This is an admin-only endpoint");
        return response;
    }
    
    @GetMapping("/public")
    public Map<String, String> publicEndpoint() {
        Map<String, String> response = new HashMap<>();
        response.put("message", "This is a public endpoint - no authentication required");
        return response;
    }
}
