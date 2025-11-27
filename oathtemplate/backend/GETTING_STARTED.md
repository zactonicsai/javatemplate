# Getting Started with Keycloak Spring Security Library

## What This Library Does

This library provides drop-in Keycloak/OAuth2 security configuration for Spring Boot applications, including:

- ✓ JWT authentication from Authorization header or cookies
- ✓ Automatic conversion of Keycloak realm roles to Spring Security authorities
- ✓ Pre-configured CORS settings for local development
- ✓ Easy customization and override capabilities

## Prerequisites

- Java 21 or higher
- Maven 3.6 or higher
- A Keycloak server (or any OAuth2/OIDC provider)
- Basic knowledge of Spring Boot and Spring Security

## 5-Minute Quick Start

### 1. Build and Install the Library

```bash
chmod +x build.sh
./build.sh
```

Or manually:
```bash
mvn clean install
```

### 2. Create a New Spring Boot Project

Create a new Spring Boot application or use an existing one.

### 3. Add Dependencies

Add to your `pom.xml`:

```xml
<dependencies>
    <!-- The library -->
    <dependency>
        <groupId>com.example</groupId>
        <artifactId>keycloak-spring-security-lib</artifactId>
        <version>1.0.0</version>
    </dependency>
    
    <!-- Required Spring Boot starters -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
    </dependency>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-security</artifactId>
    </dependency>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-oauth2-resource-server</artifactId>
    </dependency>
    <dependency>
        <groupId>org.springframework.security</groupId>
        <artifactId>spring-security-oauth2-jose</artifactId>
    </dependency>
</dependencies>
```

### 4. Create Your Application Class

```java
package com.yourcompany.yourapp;

import com.example.demo.config.SecurityConfig;
import com.example.demo.config.CorsConfig;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Import;

@SpringBootApplication
@Import({SecurityConfig.class, CorsConfig.class})
public class YourApplication {
    public static void main(String[] args) {
        SpringApplication.run(YourApplication.class, args);
    }
}
```

### 5. Configure Keycloak

Create or update `src/main/resources/application.yml`:

```yaml
spring:
  security:
    oauth2:
      resourceserver:
        jwt:
          issuer-uri: https://your-keycloak-server:8080/realms/your-realm
```

### 6. Create a Protected Endpoint

```java
package com.yourcompany.yourapp.controller;

import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class HelloController {
    
    @GetMapping("/api/hello")
    @PreAuthorize("hasRole('USER')")
    public String hello(Authentication auth) {
        return "Hello, " + auth.getName() + "!";
    }
}
```

### 7. Run Your Application

```bash
mvn spring-boot:run
```

### 8. Test It

Get a JWT token from Keycloak, then:

```bash
# Using Authorization header
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost:8080/api/hello

# Using cookie
curl -b "JSESSIONID=YOUR_JWT_TOKEN" \
     http://localhost:8080/api/hello
```

## Understanding the Components

### SecurityConfig

Provides these Spring beans:

1. **SecurityFilterChain**: Configures HTTP security rules
   - Permits `/getAuth` endpoint
   - Requires `ROLE_USER` for `/`, `/api/**`, etc.
   - Authenticates all other requests

2. **BearerTokenResolver**: Custom resolver that checks:
   - First: `Authorization: Bearer <token>` header
   - Then: `JSESSIONID` cookie

3. **JwtAuthenticationConverter**: Converts JWT to Spring Authentication
   - Extracts roles from `realm_access.roles` claim
   - Adds `ROLE_` prefix (Keycloak's `user` → `ROLE_USER`)

4. **CorsConfigurationSource**: CORS configuration
   - Default origins: `localhost:3000`, `localhost:5173`
   - Allows all methods and headers
   - Credentials enabled

### CorsConfig

Additional Web MVC CORS configuration that applies the same CORS rules.

## Customization Examples

### Change Allowed Origins

```java
@Configuration
public class CustomCorsConfig {
    
    @Bean
    @Primary
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration config = new CorsConfiguration();
        config.addAllowedOrigin("https://myapp.com");
        config.addAllowedOrigin("https://staging.myapp.com");
        config.addAllowedMethod("*");
        config.addAllowedHeader("*");
        config.setAllowCredentials(true);
        
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", config);
        return source;
    }
}
```

### Change Cookie Name

The library uses `JSESSIONID` by default. To change:

```java
@Configuration
public class CustomBearerTokenConfig {
    
    @Bean
    @Primary
    public BearerTokenResolver bearerTokenResolver() {
        return request -> {
            // Check Authorization header first
            String authHeader = request.getHeader(HttpHeaders.AUTHORIZATION);
            if (StringUtils.hasText(authHeader) && authHeader.startsWith("Bearer ")) {
                return authHeader.substring(7);
            }
            
            // Check custom cookie name
            if (request.getCookies() != null) {
                for (Cookie cookie : request.getCookies()) {
                    if ("MY_CUSTOM_COOKIE".equals(cookie.getName())) {
                        return cookie.getValue();
                    }
                }
            }
            
            return null;
        };
    }
}
```

### Add Custom Security Rules

```java
@Configuration
@EnableMethodSecurity
public class CustomSecurityConfig {
    
    @Autowired
    private BearerTokenResolver cookieAwareBearerTokenResolver;
    
    @Autowired
    private JwtAuthenticationConverter jwtAuthConverter;
    
    @Bean
    public SecurityFilterChain myCustomFilterChain(HttpSecurity http) throws Exception {
        http
            .csrf(AbstractHttpConfigurer::disable)
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/public/**").permitAll()
                .requestMatchers("/api/admin/**").hasRole("ADMIN")
                .requestMatchers("/api/**").hasAnyRole("USER", "ADMIN")
                .anyRequest().authenticated()
            )
            .oauth2ResourceServer(oauth -> oauth
                .bearerTokenResolver(cookieAwareBearerTokenResolver)
                .jwt(jwt -> jwt.jwtAuthenticationConverter(jwtAuthConverter))
            );
        
        return http.build();
    }
}
```

## Role Mapping

The library expects Keycloak to include roles in the JWT. Ensure your Keycloak client is configured:

1. Go to Keycloak Admin Console
2. Select your client
3. Go to Client Scopes → Dedicated scopes
4. Add a mapper:
   - Mapper Type: **User Realm Role**
   - Token Claim Name: `realm_access.roles`
   - Add to access token: **ON**

The library will automatically convert these to Spring Security authorities:
- Keycloak role: `user` → Spring authority: `ROLE_USER`
- Keycloak role: `admin` → Spring authority: `ROLE_ADMIN`

## Troubleshooting

### Enable Debug Logging

Add to `application.yml`:

```yaml
logging:
  level:
    com.example.demo.config: DEBUG
    org.springframework.security: DEBUG
```

### Common Issues

**Problem**: 401 Unauthorized

Solutions:
- Verify JWT is being sent (check browser dev tools or curl command)
- Confirm `issuer-uri` matches your Keycloak realm
- Check Keycloak server is running and accessible

**Problem**: 403 Forbidden

Solutions:
- User is authenticated but missing required role
- Check user has roles assigned in Keycloak
- Verify role names match (case-sensitive)
- Ensure `ROLE_` prefix is not duplicated

**Problem**: CORS errors

Solutions:
- Add your frontend URL to CORS configuration
- Ensure `allowCredentials: true` in both frontend and backend
- Check frontend is sending credentials (`credentials: 'include'`)

## Next Steps

- Review the example application in `examples/basic-app/`
- Read `INSTALLATION_GUIDE.md` for advanced topics
- Check `PROJECT_SUMMARY.md` for migration guidance
- Customize security rules for your use case

## Support and Contributing

For issues, questions, or contributions, please refer to the project repository.

## License

[Add your license information]
