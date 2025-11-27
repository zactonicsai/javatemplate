# Keycloak Spring Security Library

A reusable Spring Security configuration library for Keycloak OAuth2 Resource Server integration.

## Features

- Cookie-based and header-based JWT authentication
- Custom BearerTokenResolver that checks both Authorization header and cookies
- Keycloak realm roles to Spring Security authorities conversion
- Pre-configured CORS settings
- Spring Security configuration ready to use

## Installation

Add this library to your Spring Boot application's `pom.xml`:

```xml
<dependency>
    <groupId>com.example</groupId>
    <artifactId>keycloak-spring-security-lib</artifactId>
    <version>1.0.0</version>
</dependency>
```

## Usage

### 1. Add Required Dependencies

Your application needs these Spring Boot dependencies:

```xml
<dependencies>
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

### 2. Enable the Library

Import the configuration in your Spring Boot application:

```java
@SpringBootApplication
@Import({SecurityConfig.class, CorsConfig.class})
public class YourApplication {
    public static void main(String[] args) {
        SpringApplication.run(YourApplication.class, args);
    }
}
```

Or use component scanning:

```java
@SpringBootApplication
@ComponentScan(basePackages = {
    "com.yourpackage",
    "com.example.demo.config"
})
public class YourApplication {
    public static void main(String[] args) {
        SpringApplication.run(YourApplication.class, args);
    }
}
```

### 3. Configure Application Properties

Add your Keycloak settings to `application.yml`:

```yaml
spring:
  security:
    oauth2:
      resourceserver:
        jwt:
          issuer-uri: https://your-keycloak-server/realms/your-realm
          # OR use jwk-set-uri:
          # jwk-set-uri: https://your-keycloak-server/realms/your-realm/protocol/openid-connect/certs
```

### 4. Customize CORS Settings (Optional)

The library provides default CORS configuration for `localhost:3000` and `localhost:5173`. To customize:

**Option A:** Override the `corsConfigurationSource` bean in your application:

```java
@Configuration
public class CustomCorsConfig {
    
    @Bean
    @Primary
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration configuration = new CorsConfiguration();
        configuration.addAllowedOrigin("https://yourfrontend.com");
        configuration.addAllowedMethod("*");
        configuration.addAllowedHeader("*");
        configuration.setAllowCredentials(true);
        
        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", configuration);
        return source;
    }
}
```

**Option B:** Exclude the library's CORS config and create your own:

```java
@SpringBootApplication
@Import(SecurityConfig.class)
// Don't import CorsConfig
public class YourApplication {
    // Your custom CORS configuration
}
```

### 5. Customize Security Rules (Optional)

To override the default security configuration:

```java
@Configuration
@EnableMethodSecurity
public class CustomSecurityConfig {
    
    @Autowired
    private BearerTokenResolver cookieAwareBearerTokenResolver;
    
    @Autowired
    private JwtAuthenticationConverter jwtAuthConverter;
    
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .csrf(AbstractHttpConfigurer::disable)
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/public/**").permitAll()
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

## Configuration Components

### SecurityConfig

Provides:
- `SecurityFilterChain` - Main security configuration
- `BearerTokenResolver` - Resolves JWT from Authorization header or cookie
- `JwtAuthenticationConverter` - Converts Keycloak realm roles to Spring authorities
- `CorsConfigurationSource` - CORS configuration

### CorsConfig

Provides:
- Web MVC CORS mappings for all endpoints
- Default allowed origins: `localhost:3000`, `localhost:5173`

## Authentication Flow

1. Client sends request with JWT either:
   - In `Authorization: Bearer <token>` header, OR
   - In `JSESSIONID` cookie

2. Library extracts and validates the JWT

3. Keycloak realm roles are converted to Spring Security authorities with `ROLE_` prefix

4. Access is granted/denied based on configured rules

## Building the Library

```bash
mvn clean install
```

This will:
- Compile the library
- Run tests
- Generate JAR file
- Generate sources JAR
- Generate javadoc JAR
- Install to local Maven repository

## License

[Add your license here]
