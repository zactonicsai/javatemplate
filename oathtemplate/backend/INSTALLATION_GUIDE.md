# Installation and Usage Guide

## Building and Installing the Library

### Step 1: Build the Library

Navigate to the library directory and build it:

```bash
cd keycloak-spring-security-lib
mvn clean install
```

This will:
- Compile the library code
- Run any tests
- Package the library as a JAR
- Install it to your local Maven repository (~/.m2/repository)

The library will be installed at:
```
~/.m2/repository/com/example/keycloak-spring-security-lib/1.0.0/
```

### Step 2: Use the Library in Your Project

Add the dependency to your application's `pom.xml`:

```xml
<dependency>
    <groupId>com.example</groupId>
    <artifactId>keycloak-spring-security-lib</artifactId>
    <version>1.0.0</version>
</dependency>
```

## Quick Start Example

### 1. Create a New Spring Boot Application

```java
@SpringBootApplication
@Import({SecurityConfig.class, CorsConfig.class})
public class MyApplication {
    public static void main(String[] args) {
        SpringApplication.run(MyApplication.class, args);
    }
}
```

### 2. Configure Keycloak Connection

`application.yml`:
```yaml
spring:
  security:
    oauth2:
      resourceserver:
        jwt:
          issuer-uri: https://your-keycloak:8080/realms/myrealm
```

### 3. Create Protected Endpoints

```java
@RestController
@RequestMapping("/api")
public class MyController {
    
    @GetMapping("/protected")
    @PreAuthorize("hasRole('USER')")
    public String protectedEndpoint(Authentication auth) {
        return "Hello, " + auth.getName();
    }
}
```

### 4. Run Your Application

```bash
mvn spring-boot:run
```

## Authentication Methods

The library supports two ways to send JWT tokens:

### Method 1: Authorization Header
```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost:8080/api/protected
```

### Method 2: Cookie
```bash
curl -b "JSESSIONID=YOUR_JWT_TOKEN" \
     http://localhost:8080/api/protected
```

## Advanced Configuration

### Custom Security Rules

Override the default security configuration:

```java
@Configuration
@EnableMethodSecurity
public class CustomSecurityConfig {
    
    @Autowired
    private BearerTokenResolver cookieAwareBearerTokenResolver;
    
    @Autowired
    private JwtAuthenticationConverter jwtAuthConverter;
    
    @Bean
    public SecurityFilterChain customFilterChain(HttpSecurity http) throws Exception {
        http
            .csrf(AbstractHttpConfigurer::disable)
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/public/**").permitAll()
                .requestMatchers("/api/**").hasRole("USER")
                .requestMatchers("/admin/**").hasRole("ADMIN")
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

### Custom CORS Configuration

```java
@Configuration
public class CustomCorsConfig {
    
    @Bean
    @Primary
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration config = new CorsConfiguration();
        config.addAllowedOrigin("https://myapp.com");
        config.addAllowedOrigin("https://admin.myapp.com");
        config.addAllowedMethod("*");
        config.addAllowedHeader("*");
        config.setAllowCredentials(true);
        
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", config);
        return source;
    }
}
```

### Programmatic Security Configuration

You can also exclude the library's security config entirely and use it as a reference:

```java
@SpringBootApplication
// Don't import SecurityConfig - create your own
public class MyApplication {
    
    @Bean
    public BearerTokenResolver customBearerTokenResolver() {
        // Use the library's logic or customize it
        return new BearerTokenResolver() {
            @Override
            public String resolve(HttpServletRequest request) {
                // Your custom logic
                return null;
            }
        };
    }
}
```

## Keycloak Realm Configuration

The library expects Keycloak to provide roles in the JWT. Ensure your Keycloak realm is configured to include roles:

1. In Keycloak Admin Console, go to your client
2. Navigate to Client Scopes → Dedicated scopes
3. Add mapper for realm roles:
   - Mapper Type: User Realm Role
   - Token Claim Name: `realm_access.roles`
   - Add to ID token: ON
   - Add to access token: ON

## Troubleshooting

### Enable Debug Logging

```yaml
logging:
  level:
    com.example.demo.config: DEBUG
    org.springframework.security: DEBUG
```

### Common Issues

**Issue**: 401 Unauthorized
- Check that JWT is being sent correctly (header or cookie)
- Verify Keycloak issuer-uri is correct
- Check Keycloak realm roles are included in JWT

**Issue**: 403 Forbidden
- User is authenticated but lacks required role
- Check role names match (case-sensitive, with ROLE_ prefix)
- Verify Keycloak user has assigned roles

**Issue**: CORS errors
- Update CORS configuration with your frontend URL
- Ensure `allowCredentials` is `true` if sending cookies
- Check that frontend includes credentials in requests

## Publishing to Maven Repository

### For Internal Use (Nexus/Artifactory)

Update `pom.xml` with your repository:

```xml
<distributionManagement>
    <repository>
        <id>internal-repo</id>
        <url>https://your-nexus/repository/maven-releases/</url>
    </repository>
</distributionManagement>
```

Deploy:
```bash
mvn clean deploy
```

### For Maven Central

Follow Maven Central publishing guide:
https://central.sonatype.org/publish/publish-guide/

## License

[Add your license information]
