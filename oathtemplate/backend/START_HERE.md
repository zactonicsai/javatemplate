# Keycloak Spring Security Library

## 🎉 Your application has been converted to a reusable library!

This package contains everything you need to use your Keycloak security configuration as a Maven library in multiple projects.

## 📦 What's Inside

```
keycloak-spring-security-lib/
├── 📄 Documentation (Start Here!)
│   ├── GETTING_STARTED.md       ⭐ Read this first!
│   ├── QUICK_REFERENCE.md       Quick commands cheat sheet
│   ├── CONVERSION_SUMMARY.md    What changed from app to lib
│   ├── INSTALLATION_GUIDE.md    Detailed setup guide
│   ├── PROJECT_SUMMARY.md       Technical details
│   └── README.md               Library overview
│
├── 🔧 Library Source Code
│   ├── pom.xml                 Maven configuration
│   ├── build.sh                Build script
│   └── src/main/java/          Configuration classes
│       └── com/example/demo/config/
│           ├── SecurityConfig.java
│           └── CorsConfig.java
│
└── 📚 Examples
    └── basic-app/              Complete working example
        ├── pom.xml
        └── src/
```

## 🚀 Quick Start (3 Steps)

### 1. Build the Library
```bash
cd keycloak-spring-security-lib
./build.sh
```

### 2. Add to Your Project
In your app's `pom.xml`:
```xml
<dependency>
    <groupId>com.example</groupId>
    <artifactId>keycloak-spring-security-lib</artifactId>
    <version>1.0.0</version>
</dependency>
```

### 3. Import Configuration
```java
@SpringBootApplication
@Import({SecurityConfig.class, CorsConfig.class})
public class YourApp {
    public static void main(String[] args) {
        SpringApplication.run(YourApp.class, args);
    }
}
```

Done! Your app now has Keycloak security configured.

## 📖 Documentation Guide

**New to this library?**
→ Start with `GETTING_STARTED.md`

**Need quick commands?**
→ Check `QUICK_REFERENCE.md`

**Want to understand the conversion?**
→ Read `CONVERSION_SUMMARY.md`

**Need to customize?**
→ See `INSTALLATION_GUIDE.md`

**Want a working example?**
→ Look at `examples/basic-app/`

## ✨ Key Features

✅ **Cookie or Header Auth** - Supports both `Authorization: Bearer` and cookies
✅ **Keycloak Role Mapping** - Auto-converts realm roles to Spring authorities
✅ **CORS Ready** - Pre-configured for local development
✅ **Fully Customizable** - Override any bean in your application
✅ **Zero Boilerplate** - Just import and configure

## 🔧 What the Library Provides

When you import this library, you automatically get:

- **SecurityFilterChain** - Complete HTTP security configuration
- **BearerTokenResolver** - Extracts JWT from header or cookie  
- **JwtAuthenticationConverter** - Converts Keycloak roles to Spring authorities
- **CorsConfigurationSource** - CORS settings for your app

## 🎯 Use Cases

This library is perfect for:
- Multiple microservices needing the same Keycloak setup
- Standardizing security across team projects
- Avoiding copy-paste of security configuration
- Maintaining consistent authentication logic

## 📋 Requirements

- Java 21+
- Maven 3.6+
- Spring Boot 3.3.4
- A Keycloak server (or compatible OIDC provider)

## 🧪 Testing

The library includes a complete example application in `examples/basic-app/`.

To test:
```bash
# Build the library first
./build.sh

# Then run the example
cd examples/basic-app
# Configure Keycloak in application.yml
mvn spring-boot:run
```

## 🤝 How It Works

1. **You build**: `mvn clean install` installs to `~/.m2/repository`
2. **You add**: Add dependency to your project's `pom.xml`
3. **You import**: `@Import({SecurityConfig.class, CorsConfig.class})`
4. **You configure**: Set Keycloak URL in `application.yml`
5. **It works**: JWT authentication via header or cookie

## 🔄 From Application to Library

**Before:** Standalone Spring Boot application with security config
**After:** Reusable library providing security configuration as beans

**What changed:**
- ❌ Removed: Application class, controllers, static resources
- ✅ Kept: Security and CORS configuration classes
- 🔧 Modified: POM dependencies to `provided` scope
- 📦 Added: Source and Javadoc generation

## 📝 Example Usage

**Your application:**
```java
@SpringBootApplication
@Import({SecurityConfig.class, CorsConfig.class})
public class MyApp {
    public static void main(String[] args) {
        SpringApplication.run(MyApp.class, args);
    }
}
```

**Your controller:**
```java
@RestController
public class MyController {
    @GetMapping("/api/hello")
    @PreAuthorize("hasRole('USER')")
    public String hello(Authentication auth) {
        return "Hello, " + auth.getName();
    }
}
```

**Your config:**
```yaml
spring:
  security:
    oauth2:
      resourceserver:
        jwt:
          issuer-uri: https://keycloak/realms/myrealm
```

That's all you need!

## 🐛 Troubleshooting

**Issue:** Library not found
**Fix:** Run `mvn clean install` in the library directory

**Issue:** 401 Unauthorized  
**Fix:** Check JWT is being sent and Keycloak URL is correct

**Issue:** 403 Forbidden
**Fix:** User needs roles assigned in Keycloak

**Issue:** CORS errors
**Fix:** Update CORS configuration with your frontend URL

See `INSTALLATION_GUIDE.md` for detailed troubleshooting.

## 📚 Further Reading

- **GETTING_STARTED.md** - Comprehensive walkthrough
- **INSTALLATION_GUIDE.md** - Advanced configuration
- **QUICK_REFERENCE.md** - Command cheat sheet
- **examples/basic-app/** - Working example code

## 🎓 Next Steps

1. ✅ Extract the zip file
2. ✅ Read `GETTING_STARTED.md`
3. ✅ Run `./build.sh`
4. ✅ Try the example app
5. ✅ Use in your own project

## 📞 Support

For issues or questions:
- Check the documentation files
- Review the example application  
- Enable debug logging (see guides)

---

**Version:** 1.0.0  
**Spring Boot:** 3.3.4  
**Java:** 21+  

**Happy coding! 🚀**
