package com.example.demo.web;

import org.springframework.web.bind.annotation.*;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.annotation.AuthenticationPrincipal;

@RestController
@CrossOrigin(origins = "http://localhost:5173", allowCredentials = "true")
public class HelloController {

    @GetMapping("/api/hello")
    @PreAuthorize("hasRole('USER')")
    public String hello(@AuthenticationPrincipal Jwt jwt){
        String username = jwt.getClaimAsString("preferred_username");
        if (username == null ) {
           username = jwt.getSubject();
        }
        return "{ data: 'Hello " + username + "' } ";
    }

    @GetMapping("/api/hello/admin")
    @PreAuthorize("hasRole('ADMIN')")
    public String admin(@AuthenticationPrincipal Jwt jwt){
        String username = jwt.getClaimAsString("preferred_username");
        if (username == null ) {
           username = jwt.getSubject();
        }
        return "{ data: 'ADMIN Called " + username + "' } ";
    }

    @GetMapping("/api/hello/user")
    @PreAuthorize("hasRole('UPLOAD')")
    public String user(@AuthenticationPrincipal Jwt jwt){
        String username = jwt.getClaimAsString("preferred_username");
        if (username == null ) {
           username = jwt.getSubject();
        }
        return "{ data: 'User INFO " + username + "' } ";
    }
}
