package com.example.demo.web;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;
import org.springframework.security.core.*;
import org.springframework.security.core.context.SecurityContextHolder;
import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.stream.Collectors;

@RestController
public class AuthController {

    @Value("${app.oauth2.authorization-uri}") String authUri;
    @Value("${app.oauth2.client-id}") String clientId;
    @Value("${app.oauth2.redirect-uri}") String redirectUri;
    @Value("${app.oauth2.scope:openid profile}") String scope;

    @GetMapping("/getAuth")
    public ResponseEntity<?> getAuth(){
        Authentication a = SecurityContextHolder.getContext().getAuthentication();
        boolean ok = a != null && a.isAuthenticated() &&
            a.getAuthorities().stream().map(GrantedAuthority::getAuthority)
            .collect(Collectors.toSet()).contains("ROLE_USER");

        if (ok) return ResponseEntity.ok("Authenticated as " + a.getName());

        String url = authUri + "?response_type=code&client_id=" + clientId +
                "&redirect_uri=" + URLEncoder.encode(redirectUri, StandardCharsets.UTF_8) +
                "&scope=" + URLEncoder.encode(scope, StandardCharsets.UTF_8);

        HttpHeaders h = new HttpHeaders();
        h.setLocation(java.net.URI.create(url));
        return new ResponseEntity<>(h, HttpStatus.FOUND);
    }
}
