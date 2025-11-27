# Examples

This directory contains example applications demonstrating how to use the keycloak-spring-security-lib.

## basic-app

A minimal Spring Boot application showing:
- How to import the library configuration
- Sample protected endpoints with role-based access
- Configuration for connecting to Keycloak

### Running the Example

1. First, build and install the library:
```bash
cd ..
mvn clean install
```

2. Configure Keycloak connection in `src/main/resources/application.yml`

3. Run the example:
```bash
cd basic-app
mvn spring-boot:run
```

### Testing the Endpoints

```bash
# Get a JWT token from your Keycloak server first
TOKEN="your_jwt_token_here"

# Test with Authorization header
curl -H "Authorization: Bearer $TOKEN" http://localhost:8080/api/hello

# Test with cookie
curl -b "JSESSIONID=$TOKEN" http://localhost:8080/api/hello

# Test public endpoint (no auth required)
curl http://localhost:8080/api/public

# Test admin endpoint (requires ADMIN role)
curl -H "Authorization: Bearer $TOKEN" http://localhost:8080/api/admin
```

## Creating Your Own Application

1. Copy the `basic-app` directory as a starting point
2. Modify the package names and application name
3. Update the Keycloak configuration
4. Add your own controllers and business logic
5. Customize security rules if needed (see INSTALLATION_GUIDE.md)
