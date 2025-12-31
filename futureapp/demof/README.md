# Spring Boot CompletableFuture Demo (Java 21)

A reusable async execution service using Java's `CompletableFuture` with Spring Boot 3.2, Java 21 Virtual Threads, and Lombok `@Slf4j` logging.

## Features

- **Java 21 Virtual Threads**: Lightweight threads for I/O-bound operations
- **Reusable AsyncExecutorService**: Generic service accepting any function
- **Multiple execution patterns**: Supplier, Runnable, Function, Consumer
- **Advanced patterns**: Timeout, Fallback, Race, Parallel execution
- **Spring Boot 3.2**: Latest Spring Boot with virtual thread support
- **Lombok @Slf4j**: Clean logging without boilerplate

## Project Structure

```
async-demo/
├── pom.xml
├── src/main/
│   ├── java/com/example/asyncdemo/
│   │   ├── AsyncDemoApplication.java       # Main application
│   │   ├── config/
│   │   │   ├── AsyncConfig.java            # Thread pool + virtual threads
│   │   │   ├── AsyncProperties.java        # Configuration properties
│   │   │   ├── GlobalExceptionHandler.java # Exception handling
│   │   │   └── WebConfig.java              # CORS configuration
│   │   ├── service/
│   │   │   ├── AsyncExecutorService.java   # Generic async executor (REUSABLE)
│   │   │   └── HelloService.java           # Example usage
│   │   ├── controller/
│   │   │   └── HelloController.java        # REST endpoints
│   │   └── runner/
│   │       └── AsyncDemoRunner.java        # Startup demo
│   └── resources/
│       └── application.yml                 # Complete configuration
```

## Key Component: AsyncExecutorService

The `AsyncExecutorService` is the reusable component that wraps `CompletableFuture`. Inject it into any service and pass any function to run asynchronously.

### Available Methods

| Method | Input Type | Returns | Use Case |
|--------|-----------|---------|----------|
| `executeAsync(Supplier<T>)` | `Supplier<T>` | `CompletableFuture<T>` | Return a value (platform thread) |
| `executeAsyncVirtual(Supplier<T>)` | `Supplier<T>` | `CompletableFuture<T>` | Return a value (virtual thread) |
| `executeAsync(Runnable)` | `Runnable` | `CompletableFuture<Void>` | No return value |
| `executeAsyncVirtual(Runnable)` | `Runnable` | `CompletableFuture<Void>` | No return (virtual thread) |
| `executeAsync(Function<T,R>, T)` | `Function<T,R>` + input | `CompletableFuture<R>` | Transform input |
| `executeAsync(Consumer<T>, T)` | `Consumer<T>` + input | `CompletableFuture<Void>` | Consume input |
| `executeAllAsync(Supplier<T>...)` | Multiple suppliers | `CompletableFuture<T[]>` | Parallel (platform) |
| `executeAllAsyncVirtual(Supplier<T>...)` | Multiple suppliers | `CompletableFuture<T[]>` | Parallel (virtual) |
| `executeAndThen(Supplier<T>, Function<T,R>)` | Supplier + Function | `CompletableFuture<R>` | Chained operations |
| `executeWithTimeout(Supplier<T>, Duration)` | Supplier + timeout | `CompletableFuture<T>` | With timeout |
| `executeWithTimeoutDefault(Supplier<T>, Duration, T)` | + default value | `CompletableFuture<T>` | Timeout with fallback |
| `executeAnyAsync(Supplier<T>...)` | Multiple suppliers | `CompletableFuture<T>` | Race (first wins) |
| `executeWithFallback(Supplier<T>, Function)` | Supplier + fallback | `CompletableFuture<T>` | Exception handling |

## Usage Examples

### 1. Simple Task (No Return Value)
```java
@Autowired
private AsyncExecutorService asyncExecutor;

public void doSomething() {
    asyncExecutor.executeAsync(() -> {
         simulateWork(5000);
        log.info("Hello from async task!");
         simulateWork(5000);
    });
}
```

### 2. Return a Value
```java
public CompletableFuture<String> getData() {
    return asyncExecutor.executeAsync(() -> {
        log.info("Hello, fetching data...");
        return "Some data";
    });
}
```

### 3. Virtual Threads (Java 21) - For I/O Operations
```java
public CompletableFuture<String> fetchFromApi() {
    return asyncExecutor.executeAsyncVirtual(() -> {
        log.info("Hello from virtual thread - fetching API data...");
        // HTTP call, DB query, file I/O - ideal for virtual threads
        return httpClient.get("https://api.example.com/data");
    });
}
```

### 4. Transform Input
```java
public CompletableFuture<String> processName(String name) {
    return asyncExecutor.executeAsync(
        (String input) -> {
            log.info("Hello, processing: {}", input);
            return input.toUpperCase();
        },
        name
    );
}
```

### 5. Parallel Execution (Virtual Threads)
```java
public CompletableFuture<Object[]> fetchMultipleApis() {
    return asyncExecutor.executeAllAsyncVirtual(
        () -> { log.info("Fetching API 1"); return api1.fetch(); },
        () -> { log.info("Fetching API 2"); return api2.fetch(); },
        () -> { log.info("Fetching API 3"); return api3.fetch(); }
    );
}
```

### 6. With Timeout
```java
public CompletableFuture<String> fetchWithTimeout() {
    return asyncExecutor.executeWithTimeout(
        () -> slowOperation(),
        Duration.ofSeconds(5)
    );
}
```

### 7. With Fallback on Failure
```java
public CompletableFuture<String> fetchWithFallback() {
    return asyncExecutor.executeWithFallback(
        () -> riskyOperation(),
        ex -> "Default value on failure"
    );
}
```

### 8. Race Multiple Tasks (First Wins)
```java
public CompletableFuture<String> fetchFastest() {
    return asyncExecutor.executeAnyAsync(
        () -> fetchFromServer1(),
        () -> fetchFromServer2(),
        () -> fetchFromServer3()
    );
}
```

## Running the Application

### Prerequisites
- Java 21+
- Maven 3.6+

### Run with Maven
```bash
cd async-demo
mvn spring-boot:run
```

### Run JAR
```bash
mvn clean package
java -jar target/async-demo-1.0.0.jar
```

## REST API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/hello` | Simple async hello |
| GET | `/api/hello/virtual` | Virtual thread hello (Java 21) |
| GET | `/api/hello/greet?name=X` | Greet with name |
| GET | `/api/hello/greet/virtual?name=X` | Virtual thread greet |
| GET | `/api/hello/transform?name=X` | Transform name |
| POST | `/api/hello/log` | Log a message |
| GET | `/api/hello/parallel` | Parallel tasks (platform) |
| GET | `/api/hello/parallel/virtual` | Parallel tasks (virtual) |
| GET | `/api/hello/chain?name=X` | Chained operations |
| GET | `/api/hello/timeout?name=X&timeoutMs=1000` | With timeout |
| GET | `/api/hello/fallback?name=X&fail=false` | With fallback |
| GET | `/api/hello/race` | Race (first wins) |

## Monitoring Endpoints

| Endpoint | Description |
|----------|-------------|
| `/actuator/health` | Health check |
| `/actuator/info` | Application info |
| `/actuator/metrics` | Metrics |

## Configuration (application.yml)

```yaml
spring:
  threads:
    virtual:
      enabled: true  # Enable virtual threads for Spring MVC

async:
  executor:
    core-pool-size: 4
    max-pool-size: 8
    queue-capacity: 100
```

## When to Use Virtual Threads vs Platform Threads

| Use Case | Thread Type |
|----------|-------------|
| HTTP API calls | Virtual |
| Database queries | Virtual |
| File I/O | Virtual |
| Network operations | Virtual |
| CPU-intensive work | Platform |
| Heavy computations | Platform |

## Requirements

- Java 21+
- Maven 3.6+
- Spring Boot 3.2.0
