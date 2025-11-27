# Quick Reference Card

## Build & Install

```bash
./build.sh
# or
mvn clean install
```

## Add to Your Project

**pom.xml:**
```xml
<dependency>
    <groupId>com.example</groupId>
    <artifactId>keycloak-spring-security-lib</artifactId>
    <version>1.0.0</version>
</dependency>
```

## Import Configuration

**YourApplication.java:**
```java
@SpringBootApplication
@Import({SecurityConfig.class, CorsConfig.class})
public class YourApplication {
    public static void main(String[] args) {
        SpringApplication.run(YourApplication.class, args);
    }
}
```

## Configure Keycloak

**application.yml:**
```yaml
spring:
  security:
    oauth2:
      resourceserver:
        jwt:
          issuer-uri: https://your-keycloak/realms/your-realm
```

## Test Authentication

```bash
# Get JWT from Keycloak first
TOKEN="eyJhbGc..."

# Test with header
curl -H "Authorization: Bearer $TOKEN" http://localhost:8080/api/hello

# Test with cookie
curl -b "JSESSIONID=$TOKEN" http://localhost:8080/api/hello
```

## Use in Controllers

```java
@GetMapping("/api/protected")
@PreAuthorize("hasRole('USER')")
public String protectedEndpoint(Authentication auth) {
    return "Hello, " + auth.getName();
}
```

## Common Customizations

### Change CORS Origins
```java
@Bean
@Primary
public CorsConfigurationSource corsConfigurationSource() {
    CorsConfiguration config = new CorsConfiguration();
    config.addAllowedOrigin("https://myapp.com");
    // ... rest of config
}
```

### Override Security Rules
```java
@Bean
public SecurityFilterChain filterChain(HttpSecurity http) {
    http.authorizeHttpRequests(auth -> auth
        .requestMatchers("/public/**").permitAll()
        .requestMatchers("/admin/**").hasRole("ADMIN")
        .anyRequest().authenticated()
    );
    // ... rest of config
}
```

## Troubleshooting

**401 Unauthorized:**
- Check JWT is being sent correctly
- Verify issuer-uri is correct
- Ensure Keycloak is accessible

**403 Forbidden:**
- User authenticated but missing role
- Check role names (case-sensitive)
- Verify user has roles in Keycloak

**CORS Errors:**
- Add frontend URL to CORS config
- Enable credentials on both sides
- Check browser console for details

## Enable Debug Logging

```yaml
logging:
  level:
    com.example.demo.config: DEBUG
    org.springframework.security: DEBUG
```

## Documentation

- `GETTING_STARTED.md` - Start here!
- `INSTALLATION_GUIDE.md` - Detailed setup
- `PROJECT_SUMMARY.md` - What changed
- `CONVERSION_SUMMARY.md` - Complete overview
- `examples/basic-app/` - Working example

## Role Mapping

Keycloak → Spring Security:
- `user` → `ROLE_USER`
- `admin` → `ROLE_ADMIN`
- Custom roles get `ROLE_` prefix automatically

## What the Library Provides

✓ SecurityFilterChain
✓ BearerTokenResolver (header + cookie)
✓ JwtAuthenticationConverter
✓ CorsConfigurationSource
✓ Pre-configured security rules

## File Structure

```
keycloak-spring-security-lib/
├── pom.xml
├── build.sh
├── src/main/java/
│   └── com/example/demo/config/
│       ├── SecurityConfig.java
│       └── CorsConfig.java
└── examples/
    └── basic-app/
```

---

**Version:** 1.0.0
**Spring Boot:** 3.3.4
**Java:** 21+
