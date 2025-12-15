# HTMX Person Manager + SQS Demo (Spring Boot)

This project is a **Spring Boot 3.5.x** demo app that shows how to:

- Manage a `Person` table in **PostgreSQL** via a REST API
- Drive a modern **Tailwind CSS + vanilla JS** UI page that calls that API
- Integrate with **AWS SQS (via LocalStack)** to send and receive messages
- Use **Liquibase** to manage database schema and seed data
- Write **unit tests** around the SQS sender and listener components

The app is currently named **`Task Manager`** in configuration, but the active domain model is `Person` (older `Task` classes are kept as `.old` reference files).

---

## 1. Tech Stack

**Back end**

- Java (JDK 17+ recommended for Spring Boot 3.5.x)
- Spring Boot 3.5.8
  - `spring-boot-starter-web` – REST API
  - `spring-boot-starter-actuator` – health/info endpoints
  - `spring-boot-starter-thymeleaf` – template engine (not heavily used; main UI is static HTML in `/static`)
  - `spring-boot-starter-data-jpa` – JPA/Hibernate for `Person` entity
  - `spring-boot-starter-validation` – Bean validation support
- **Liquibase** – database migrations, schema creation, and sample data
- **PostgreSQL** – main database
- **AWS SDK v2 for SQS** – `software.amazon.awssdk:sqs`
- **Lombok** – `@Data`, `@Builder`, `@NoArgsConstructor`, `@AllArgsConstructor`, `@RequiredArgsConstructor`
- **JUnit 5 + Mockito + AssertJ** – unit tests for SQS services

**Front end**

- Static HTML in `src/main/resources/static/index.html`
- Tailwind CSS (via CDN)
- Font Awesome icons
- Vanilla JS calling `http://localhost:8080/api/persons`

---

## 2. High-Level Architecture

### Domain: Person Management

Files:

- `model/entity/Person.java`
- `model/dto/PersonDTO.java`
- `model/mapper/PersonMapper.java`
- `repository/PersonRepository.java`
- `service/PersonService.java`
- `controller/PersonController.java`

Flow:

1. **HTTP request** hits `PersonController` (`/api/persons`).
2. Controller delegates to `PersonService`.
3. `PersonService` uses `PersonRepository` (Spring Data JPA) to interact with Postgres.
4. Entities (`Person`) are mapped to DTOs (`PersonDTO`) via `PersonMapper`.
5. JSON DTOs are returned to the browser.

### SQS Messaging

Files:

- `config/SqsConfig.java`
- `config/SqsQueueInitializer.java`
- `service/SqsSenderService.java`
- `service/SqsListenerService.java`
- `controller/SqsController.java`

Flow:

1. `SqsConfig` builds a **singleton `SqsClient`** using Spring `@Configuration` + `@Bean`,
   reading `aws.region` and `aws.endpoint` from `application.yml`, and using static test credentials.
2. `SqsQueueInitializer` runs at startup (`@PostConstruct`) to:
   - Check if the configured queue exists.
   - Create it if missing.
3. `SqsSenderService` sends messages to the configured queue URL.
4. `SqsController` exposes an HTTP endpoint:
   - `POST /sqs/send?message=...` → calls `SqsSenderService.sendMessage(...)`.
5. `SqsListenerService` uses `@Scheduled` to poll the queue periodically:
   - Calls `receiveMessage` with a `ReceiveMessageRequest`.
   - Logs received messages using `@Slf4j`.
   - Deletes messages from the queue via `deleteMessage` to prevent re-delivery.

> SQS is typically intended to run against **LocalStack** in dev, configured via `aws.endpoint` in `application.yml`.

### UI / Front End

File:

- `src/main/resources/static/index.html`

Key points:

- A single-page “Person Management” UI using Tailwind and Font Awesome.
- JavaScript uses `fetch` to call the REST API at `http://localhost:8080/api/persons`.
- Features:
  - **List** all persons in a table.
  - **Add** a new person via a modal form.
  - **Edit** an existing person.
  - **Delete** a person (with confirmation).
  - Shows a record count and “Last updated” timestamp.
  - Simple toast notifications for success/error.

---

## 3. Configuration (`application.yml`)

Location: `src/main/resources/application.yml`

```yaml
spring:
  application:
    name: Task Manager

  datasource:
    url: ${SPRING_DATASOURCE_URL:jdbc:postgresql://localhost:5432/taskdb}
    username: ${SPRING_DATASOURCE_USERNAME:taskuser}
    password: ${SPRING_DATASOURCE_PASSWORD:taskpass}
    driver-class-name: org.postgresql.Driver

  thymeleaf:
    cache: false

server:
  port: 8080

# (JPA and Liquibase config in this section; some JPA settings are commented out)

aws:
  region: us-east-1
  endpoint: http://localstack:4566
  sqs:
    queue-name: updates
    queue-url: http://localstack:4566/000000000000/updates


# Docker Setup for HTMX Spring Boot App

This project uses **Docker** and **Docker Compose** to run:

- A **PostgreSQL** database
- The **Spring Boot HTMX app**
- **LocalStack** to emulate AWS services (S3, DynamoDB, SQS, Lambda)

The key files are:

- `Dockerfile` – how to build the Spring Boot app image
- `docker-compose.yml` – how to run all the containers together

---

## 1. How Docker Fits This App

At a high level:

- **Dockerfile** defines a *custom image* for the Spring Boot application.
- **docker-compose.yml** defines *services*:
  - `postgres` – database
  - `spring-app` – your Java app (built from `Dockerfile`)
  - `localstack` – local AWS emulator for S3/SQS/etc.
- Docker Compose wires them together with:
  - **Networks** – so containers can talk to each other by name (`postgres`, `localstack`, `spring-app`)
  - **Volumes** – to persist data (Postgres DB, LocalStack state)
  - **Environment variables** – to configure each container

From your working directory:

```bash
cd C:\Users\solarisone\javatemplate\htmxapp
docker compose up --build
Great — here is a **single, complete README.md** that includes **everything**:

✅ Full explanation of your **Java Spring App**
✅ Full explanation of your **Dockerfile**
✅ Full explanation of your **docker-compose.yml**
✅ How Docker, the app, the DB, and LocalStack all work together
✅ What Java/Spring features are used
✅ Deep-dive setup + commands
✅ TODO test backlog

---

# **README.md — HTMX Spring Boot + Docker + LocalStack**

This project is a complete **Spring Boot 3.5.x application** powered by:

* A PostgreSQL database
* A Tailwind/HTMX front-end
* AWS SQS integration (running locally via LocalStack)
* Liquibase for DB migrations
* Docker + Docker Compose to provide a fully self-contained dev environment

This README explains **EVERY part** of the system:

1. The **Java/Spring application**
2. The **Dockerfile**
3. The **docker-compose.yml**
4. How Docker networking, volumes, and environment variables configure the app
5. Testing strategy + TODO section

---

# ⚙️ 1. Application Overview

The app contains:

### ✔️ **Person Management API**

* CRUD operations for `Person`
* DTO + Mapper layer
* Repository layer using JPA
* Service layer for logic
* Controller exposing `/api/persons`

### ✔️ **SQS Messaging**

* Sender service sends messages to SQS
* Listener service polls SQS automatically
* Queue autogeneration via `SqsQueueInitializer`
* Configurable LocalStack endpoint

### ✔️ **Front-end**

* `index.html`
* Tailwind UI
* Modal forms
* JS fetch calls to `/api/persons`

### ✔️ **Liquibase**

* Creates the `person` table
* Inserts initial sample data
* Runs automatically on container start

---

# 📁 2. Project Structure (Important Directories)

```
src/main/java/
   ├── config/   (SQS client config, Queue initializer)
   ├── controller/
   ├── model/ (DTO, Entity, Mapper)
   ├── repository/
   ├── service/
   └── HtmxAppApplication.java

src/main/resources/
   ├── application.yml
   ├── db/changelog/ (Liquibase)
   ├── static/index.html

Dockerfile
docker-compose.yml
README.md   ← This file
```

---

# 🚀 3. Dockerfile Explained

This project uses a **multi-stage Docker build**.

## **Stage 1 — Builder (Maven)**

```dockerfile
FROM maven as builder
WORKDIR /app
COPY pom.xml .
RUN mvn dependency:go-offline
COPY src ./src
RUN mvn package -DskipTests
```

### 🔍 What this does:

| Line                            | Meaning                                       |
| ------------------------------- | --------------------------------------------- |
| `FROM maven as builder`         | Starts a Maven container for building the app |
| `WORKDIR /app`                  | Sets working directory                        |
| `COPY pom.xml .`                | Copy Maven config                             |
| `RUN mvn dependency:go-offline` | Pre-download dependencies (cached)            |
| `COPY src ./src`                | Copy source code                              |
| `RUN mvn package -DskipTests`   | Build JAR file                                |

---

## **Stage 2 — Runtime (OpenJDK)**

```dockerfile
FROM openjdk:26-ea-jdk
WORKDIR /app
COPY --from=builder /app/target/htmxapp-v1.jar app.jar
CMD ["java", "-jar", "app.jar"]
EXPOSE 8080
```

### 🔍 What this does:

| Line                              | Meaning                           |
| --------------------------------- | --------------------------------- |
| `FROM openjdk`                    | Small runtime image with only JDK |
| `COPY --from=builder`             | Copies the JAR from Stage 1       |
| `CMD ["java", "-jar", "app.jar"]` | Launches Spring Boot              |
| `EXPOSE 8080`                     | Documents the web port            |

This produces a **clean** production-ready container.

---

# 🐳 4. docker-compose.yml Explained

Here is how Compose runs your entire system:

---

## **Service 1: PostgreSQL**

```yaml
postgres:
  image: postgres:18-alpine
  environment:
    POSTGRES_DB: taskdb
    POSTGRES_USER: taskuser
    POSTGRES_PASSWORD: taskpass
  ports:
    - "5432:5432"
  volumes:
    - postgres-data:/var/lib/postgresql/data
  networks:
    - app-network
```

### 🔍 What this does:

✔ Creates the database
✔ Makes it reachable as `postgres` inside Docker
✔ Exposes it to your PC via `localhost:5432`
✔ Persists DB data via `postgres-data` volume

---

## **Service 2: Spring Boot App**

```yaml
spring-app:
  build: .
  container_name: spring-app
  ports:
    - "8080:8080"
  depends_on:
    - postgres
    - localstack
  environment:
    SPRING_DATASOURCE_URL: jdbc:postgresql://postgres:5432/taskdb
    SPRING_DATASOURCE_USERNAME: taskuser
    SPRING_DATASOURCE_PASSWORD: taskpass
    AWS_REGION: us-east-1
    AWS_ENDPOINT: http://localstack:4566
  networks:
    - app-network
```

### 🔍 What this does:

✔ Builds the app using the `Dockerfile`
✔ Exposes the app at **[http://localhost:8080](http://localhost:8080)**
✔ Connects to `postgres` using Docker-internal hostname
✔ Configures AWS SDK to use LocalStack

---

## **Service 3: LocalStack**

```yaml
localstack:
  image: localstack/localstack:latest
  environment:
    SERVICES: s3,dynamodb,sqs,lambda
    AWS_DEFAULT_REGION: us-east-1
  ports:
    - "4566:4566"
  volumes:
    - "./localstack:/var/lib/localstack"
    - "/var/run/docker.sock:/var/run/docker.sock"
  networks:
    - app-network
```

### 🔍 What this does:

✔ Runs AI-style AWS
✔ Provides SQS, S3, Lambda, DynamoDB
✔ Your Java app points to it via `AWS_ENDPOINT=http://localstack:4566`
✔ Persists SQS messages / S3 uploads into `./localstack`

---

# 🔗 5. How Docker Networking Ties Everything Together

| Container   | Hostname inside Docker | Purpose    |
| ----------- | ---------------------- | ---------- |
| Postgres    | `postgres`             | Database   |
| Spring Boot | `spring-app`           | API server |
| LocalStack  | `localstack`           | Fake AWS   |

The app uses:

```
jdbc:postgresql://postgres:5432/taskdb
```

NOT `localhost` because containers talk to **each other**, not to your machine.

---

# 🧩 6. How Environment Variables Map to Spring Boot

### In docker-compose:

```
SPRING_DATASOURCE_URL=jdbc:postgresql://postgres:5432/taskdb
AWS_ENDPOINT=http://localstack:4566
```

### In application.yml:

```yaml
spring.datasource.url: ${SPRING_DATASOURCE_URL}
aws.region: ${AWS_REGION}
aws.endpoint: ${AWS_ENDPOINT}
```

Spring automatically injects the values.

---

# ▶️ 7. Running the Full Stack

### **Start everything**

```bash
docker compose up --build
```

### **Run in background**

```bash
docker compose up -d
```

### **Stop everything**

```bash
docker compose down
```

### **Reset all volumes**

```bash
docker compose down -v
```

### **View logs**

```bash
docker compose logs -f spring-app
```

---

# 🧪 8. Tests & What’s Already Included

### ✔ Existing tests:

* SqsSenderServiceTest
* SqsListenerServiceTest
* Application context load test

These use Mockito + ReflectionTestUtils to simulate AWS SQS.

---

# 📌 9. TODO — What Tests Should Be Added

### **Unit tests**

* PersonMapperTest
* PersonServiceTest (mock repository)
* PersonControllerTest (@WebMvcTest)
* Validation tests

### **Integration tests**

* Testcontainers PostgreSQL + Liquibase
* Testcontainers LocalStack for SQS roundtrip

### **E2E tests**

* Playwright/Cypress tests for the index.html UI
* Full person creation/edit/delete cycle

### **Resilience tests**

* SQS unavailable → retry or fail gracefully
* Connection issues with Postgres

---

# 🏁 10. Summary

This README gives you:

* Full explanation of the **application architecture**
* Deep detail about the **Dockerfile** and **multi-stage build**
* Every part of the **docker-compose.yml and networking**
* How the Java app uses DB + SQS + LocalStack
* How to run, debug, and extend the system
* Next steps to harden the project with more tests


