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
