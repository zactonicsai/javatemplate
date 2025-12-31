package com.example.demo.config;

import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpHeaders;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configurers.AbstractHttpConfigurer;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.oauth2.server.resource.authentication.JwtAuthenticationConverter;
import org.springframework.security.oauth2.server.resource.authentication.JwtGrantedAuthoritiesConverter;
import org.springframework.security.oauth2.server.resource.web.BearerTokenResolver;
import org.springframework.security.web.SecurityFilterChain;

import org.springframework.security.core.GrantedAuthority;
import org.springframework.security.core.authority.SimpleGrantedAuthority;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.util.StringUtils;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;

import java.util.*;

@Configuration
@EnableMethodSecurity
public class SecurityConfig {

    private static final Logger log = LoggerFactory.getLogger(SecurityConfig.class);

    private static final String ACCESS_TOKEN_COOKIE_NAME = "JSESSIONID";

    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration configuration = new CorsConfiguration();
        
        // **1. Define allowed origins** - Replace with your actual frontend URLs
        configuration.addAllowedOrigin("http://localhost:3000"); 
        configuration.addAllowedOrigin("http://localhost:5173");
        
        // **2. Define allowed methods**
        configuration.addAllowedMethod("*"); // Allow all methods (GET, POST, PUT, DELETE, etc.)
        
        // **3. Define allowed headers**
        configuration.addAllowedHeader("*"); // Allow all headers
        
        // **4. Allow credentials** - Important for cookies and JWT in headers (if applicable)
        configuration.setAllowCredentials(true); 
        
        // **5. Define how long the pre-flight request can be cached (in seconds)**
        // configuration.setMaxAge(3600L); // Optional

        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        // Apply this CORS configuration to all paths
        source.registerCorsConfiguration("/**", configuration); 
        return source;
    }
    
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        log.info("Configuring HTTP security (resource server + cookie-based JWT)");

        http
            .csrf(AbstractHttpConfigurer::disable)  .cors(cors -> cors.configurationSource(corsConfigurationSource())) 
            // Let Spring create a session for request cache, but auth itself is still via JWT
            .sessionManagement(sm ->
                sm.sessionCreationPolicy(SessionCreationPolicy.IF_REQUIRED)
            ) 
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/getAuth").permitAll()
                .requestMatchers("/", "/api/**", "/css/**", "/js/**", "/images/**")
                    .hasRole("USER")
                .anyRequest().authenticated()
            )
            .oauth2ResourceServer(oauth -> oauth
                .bearerTokenResolver(cookieAwareBearerTokenResolver())
                .jwt(jwt -> jwt.jwtAuthenticationConverter(jwtAuthConverter()))
            );

        return http.build();
    }

    /**
     * Custom BearerTokenResolver:
     * 1) Try Authorization: Bearer xxx header
     * 2) If missing, try cookie ACCESS_TOKEN
     */
    @Bean
    public BearerTokenResolver cookieAwareBearerTokenResolver() {
        return new BearerTokenResolver() {
            @Override
            public String resolve(HttpServletRequest request) {
                // 1. Standard Authorization header
                String authHeader = request.getHeader(HttpHeaders.AUTHORIZATION);
                if (StringUtils.hasText(authHeader) && authHeader.startsWith("Bearer ")) {
                    String token = authHeader.substring(7);
                    if (log.isDebugEnabled()) {
                        log.debug("Resolved JWT from Authorization header");
                    }
                    return token;
                }

                // 2. Custom cookie
                if (request.getCookies() != null) {
                    for (Cookie cookie : request.getCookies()) {
                        if (ACCESS_TOKEN_COOKIE_NAME.equals(cookie.getName())
                                && StringUtils.hasText(cookie.getValue())) {
                            if (log.isDebugEnabled()) {
                                log.debug("Resolved JWT from cookie {}", ACCESS_TOKEN_COOKIE_NAME);
                            }
                            return cookie.getValue();
                        }
                    }
                }

                if (log.isDebugEnabled()) {
                    log.debug("No bearer token found (header or cookie)");
                }
                return null;
            }
        };
    }

    @Bean
    public JwtAuthenticationConverter jwtAuthConverter() {
        JwtGrantedAuthoritiesConverter base = new JwtGrantedAuthoritiesConverter();
        base.setAuthorityPrefix("ROLE_");
        base.setAuthoritiesClaimName("roles");

        JwtAuthenticationConverter conv = new JwtAuthenticationConverter();
        conv.setJwtGrantedAuthoritiesConverter(jwt -> {
            Set<GrantedAuthority> auths = new HashSet<>(base.convert(jwt));

            Map<String, Object> realm = jwt.getClaim("realm_access");
            if (realm != null) {
                @SuppressWarnings("unchecked")
                List<String> roles = (List<String>) realm.get("roles");
                if (roles != null) {
                    roles.forEach(r -> auths.add(new SimpleGrantedAuthority("ROLE_" + r.toUpperCase())));
                }
            }

            if (log.isDebugEnabled()) {
                log.debug("JWT subject: {}", jwt.getSubject());
                log.debug("JWT authorities resolved: {}", auths);
            }

            return auths;
        });
        return conv;
    }
}
