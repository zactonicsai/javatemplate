# GitLab Issues Backlog: Error Handling Remediation

Below is a prioritized backlog of epics and issues for bringing a Spring Boot application with limited error handling up to the architectural standards outlined in the best practices document. I've structured this as epics containing stories, with suggested labels and priority indicators.

---

## EPIC 1: Foundational Exception Architecture

**[P0] Establish core exception hierarchy with Java 21 sealed classes**
Create `ApplicationException` base with sealed subclasses (Business, Integration, Security, DataAccess, Transient, Workflow). Include errorCode, correlationId, severity, and context map on all exceptions. Replace ad-hoc RuntimeException usage across codebase.

**[P0] Implement correlation ID generation and MDC propagation filter**
Add servlet filter that generates/extracts correlation IDs from `X-Correlation-ID` header, injects into MDC, and echoes in response headers. Include W3C traceparent propagation.

**[P0] Create error code registry and documentation**
Establish centralized enum or registry of stable error codes (e.g., `AUTH_001`, `PAY_INSUFFICIENT_FUNDS`). Document in `/docs/error-codes.md` with consumer-facing descriptions and remediation guidance.

**[P1] Define ErrorSeverity taxonomy and routing rules**
Classify errors as LOW/MEDIUM/HIGH/CRITICAL with automated alert routing. Wire severity into structured logging and PagerDuty/Opsgenie integration.

---

## EPIC 2: Global Exception Handler and RFC 7807

**[P0] Implement GlobalExceptionHandler with @RestControllerAdvice**
Replace default Spring error handling with centralized handler returning RFC 7807 ProblemDetail responses. Map each exception subclass to appropriate HTTP status and response shape.

**[P0] Implement error response sanitization**
Strip stack traces, internal hostnames, SQL fragments, connection strings, and PII from all outbound error responses. Add unit tests asserting sensitive data never appears in ProblemDetail output.

**[P1] Add validation error handler for @Valid/@Validated failures**
Handle `MethodArgumentNotValidException` and `ConstraintViolationException` with structured field-level error responses. Return 400 with field names but never echo submitted values.

**[P1] Implement error response content negotiation**
Support `application/problem+json` and `application/problem+xml` per client Accept header. Default to JSON.

**[P2] Create error response contract tests**
Pact or Spring Cloud Contract tests locking down error response schemas to prevent breaking changes across releases.

---

## EPIC 3: Keycloak and OIDC Hardening

**[P0] Implement custom AuthenticationEntryPoint with WWW-Authenticate**
Return RFC 6750-compliant 401 responses with proper `Bearer error=` parameter for invalid_token, insufficient_scope, and invalid_request scenarios.

**[P0] Configure JWK rotation handling with cache refresh on signature failure**
Tune NimbusJwtDecoder cache TTL to align with Keycloak key rotation. Implement single forced-refresh on signature validation failure before rejecting token.

**[P0] Add circuit breaker around Keycloak admin client calls**
Wrap all admin API calls with Resilience4j. Configure fail-closed fallback that denies access rather than defaulting to allow on Keycloak outage.

**[P1] Implement distinct handlers for 401 vs 403 scenarios**
Separate handling for no credentials, invalid token, insufficient role (RBAC), insufficient claims (CBAC), and ABAC denial. Each with appropriate audit logging.

**[P1] Add step-up authentication challenge support**
Return acr_values challenge per OIDC spec when higher assurance level required for sensitive operations.

**[P2] Implement token introspection fallback for opaque tokens**
Support RFC 7662 introspection endpoint as fallback when JWT validation fails due to non-JWT token format.

---

## EPIC 4: PostgreSQL Error Handling

**[P0] Map SQLState codes to domain exceptions**
Create translator converting unique_violation (23505) → 409 Conflict, foreign_key_violation (23503) → 409/422, check_violation (23514) → 422, with stable error codes.

**[P0] Implement retry logic for transient database errors**
Retry serialization failures (40001) and deadlocks (40P01) with exponential backoff and jitter. Max 3 attempts. Use Spring Retry or Resilience4j.

**[P0] Configure timeouts at every layer**
Set statement_timeout on database role, @Transactional(timeout), HikariCP connectionTimeout/validationTimeout, and JDBC socketTimeout. Document defaults per operation type.

**[P1] Add HikariCP pool saturation metrics and alerts**
Expose active/idle/pending/timeoutCount via Micrometer. Alert when pending connections exceed threshold or when timeouts spike.

**[P1] Return 503 with Retry-After on connection pool exhaustion**
Catch `SQLTransientConnectionException` and return proper backpressure signal to clients rather than generic 500.

**[P2] Add RDS/Aurora failover handling**
Configure AWS JDBC Driver for cluster-aware failover. Handle reader/writer role changes gracefully. Subscribe to RDS events via EventBridge.

---

## EPIC 5: Elasticsearch Resilience

**[P0] Implement partial shard failure inspection**
Check `_shards.failed` count on every search response. Define policy per endpoint: accept degraded, retry, or fail. Log all partial failures for trend analysis.

**[P1] Add circuit breaker and database fallback for critical search paths**
Wrap ES calls with `@CircuitBreaker` and fallback method querying database for critical user-facing searches.

**[P1] Implement graceful degradation for non-critical search features**
Return empty results with degradation flag for suggestions, analytics, and recommendations when ES is unavailable. Never fail user request.

**[P1] Handle version conflicts with automatic retry**
Catch 409 version conflicts on updates, refetch latest document version, reapply business logic, retry write.

**[P2] Add mapping drift detection and alerting**
Alert on 400 mapping exceptions as they indicate schema drift. Never retry these.

---

## EPIC 6: Temporal.io Workflow Hardening

**[P0] Classify activity exceptions as retryable vs non-retryable**
Audit all activities. Wrap business errors in `ApplicationFailure.newNonRetryableFailure()`. Let infrastructure exceptions propagate for Temporal retry.

**[P0] Configure explicit RetryPolicy per activity**
Remove default retry policies. Set maximumAttempts, initialInterval, backoffCoefficient, and nonRetryableErrorTypes per activity based on idempotency and criticality.

**[P0] Audit workflow code for exception swallowing**
Find any try/catch blocks in workflow code that don't rethrow or use Saga. These break determinism. Replace with Saga compensation.

**[P1] Implement Saga compensation for multi-step workflows**
Refactor workflows with multiple external side effects to use Temporal Saga pattern with reverse-order compensation.

**[P1] Add heartbeats to long-running activities**
Any activity exceeding 60 seconds must heartbeat. Set heartbeatTimeout to 3x heartbeat interval. Checkpoint progress for resumability.

**[P1] Handle Temporal client-side exceptions**
Treat `WorkflowExecutionAlreadyStarted` as success when idempotent. Handle `WorkflowNotFoundException` and `WorkflowServiceException` with circuit breaker.

**[P2] Add gRPC deadlines to all Temporal client calls**
Never allow unbounded waits. Configure timeouts on all start/signal/query operations.

---

## EPIC 7: Async and CompletableFuture Safety

**[P0] Audit and fix unbounded .get() calls**
Replace all `.get()` with `.get(timeout, unit)` or `.orTimeout(duration)`. Unbounded waits cause thread exhaustion.

**[P0] Ensure all CompletableFuture chains terminate with error handler**
Every chain must end with `.exceptionally()` or `.whenComplete()`. Silent failures from unhandled exceptions are unacceptable.

**[P1] Propagate MDC context across async boundaries**
Wrap executors with MDC-aware decorators so correlation IDs survive thread transitions. Update `CompletableFuture.supplyAsync()` call sites.

**[P1] Replace ForkJoinPool.commonPool with named executors**
Create dedicated virtual thread executors per workload category. Configure monitoring and naming for thread pool isolation.

**[P2] Migrate new async code to StructuredTaskScope**
Establish pattern for Java 21 structured concurrency in new fan-out code. Document when to prefer over CompletableFuture chains.

---

## EPIC 8: Long-Running Process Patterns

**[P0] Convert synchronous long-running endpoints to async command pattern**
Identify endpoints exceeding 5 seconds p99. Convert to `202 Accepted` with Location header pointing to status resource.

**[P1] Implement status polling and WebSocket/SSE update endpoints**
Provide client visibility into long-running work. Support both polling and push notification patterns.

**[P1] Migrate ad-hoc scheduled jobs to Temporal workflows**
Replace `@Scheduled` annotations and custom executors for durable work with Temporal workflows.

**[P2] Implement dead letter queue handling for unrecoverable failures**
Route exhausted retries to DLQ with alerting. Build admin UI for human-triggered replay.

---

## EPIC 9: AWS Service Error Handling

**[P0] Configure AWS SDK v2 retry strategy per service**
Set deliberate retry policies with jittered backoff. Configure per-service timeouts. Monitor retry metrics.

**[P0] Implement S3 error handling**
Distinguish NoSuchKey (404) from NoSuchBucket (page on-call). Handle 503 SlowDown, checksum mismatches, and PreconditionFailed. Abort incomplete multipart uploads in finally blocks.

**[P0] Add credential refresh handling**
Catch `ExpiredTokenException`, refresh credentials via IRSA/instance profile, retry once. Never silently fail on AccessDeniedException.

**[P1] Implement SQS batch partial failure handling**
Inspect `BatchResultErrorEntry` on every batch operation. Handle partial failures explicitly rather than assuming success.

**[P1] Configure SQS visibility timeout management**
Extend visibility dynamically via `ChangeMessageVisibility` for long-running processing. Tune DLQ maxReceiveCount.

**[P1] Implement SNS outbox pattern for critical notifications**
Write to local outbox table on SNS failure, retry from outbox asynchronously. Guarantee delivery for critical messages.

**[P1] Add KMS data key caching**
Use AWS Encryption SDK with bounded TTL and usage count. Page on-call for `KMSInvalidStateException` and `AccessDeniedException`.

**[P1] Implement Secrets Manager caching with fail-to-stale**
Cache secrets 5-15 minutes. Continue serving cached value on fetch failure rather than failing requests. Scrub secret names from logs.

**[P2] Wrap CloudWatch/observability calls with swallow-and-log**
Metrics publishing failures must never fail business logic. Use bounded async queues.

**[P2] Add EventBridge subscription for RDS events**
Alert on failover, storage pressure, and parameter drift events.

---

## EPIC 10: Zero-Trust Authorization (RBAC/CBAC/ABAC)

**[P0] Implement fail-closed authorization at Data Access Layer**
Audit every authorization code path. Any error, missing attribute, or PDP unavailability must result in access denied, never allowed.

**[P0] Build layered authorization enforcement**
Implement RBAC (role check) → CBAC (claims check) → ABAC (attribute evaluation) pipeline with clear boundaries and audit at each layer.

**[P0] Add tamper-evident audit logging for all security decisions**
Log grants and denials with subject, resource, action, attributes, policy version, decision, correlation ID. Ship to restricted observability stream.

**[P1] Return 404 instead of 403 for sensitive resources**
Prevent resource enumeration attacks on confidential data. Configure per resource type. Maintain internal 403/404 distinction in audit logs.

**[P1] Implement PostgreSQL row-level security (RLS) policies**
Add RLS policies with session context variables carrying subject identity and tenant ID. Defense-in-depth beyond application-layer checks.

**[P1] Add consistent-time response for security endpoints**
Prevent timing-based enumeration by applying consistent response time to auth-sensitive endpoints.

**[P2] Integrate with external PDP (OPA, Cedar)**
Externalize complex ABAC policies to dedicated policy engine with circuit breaker and cached fallback decisions.

---

## EPIC 11: External Service Integration

**[P0] Add Resilience4j circuit breakers to all external dependencies**
Configure per-service circuit breakers with appropriate failure rate thresholds, wait duration, and half-open call limits.

**[P0] Implement bulkhead isolation for external calls**
Partition thread pools per external dependency so a slow service cannot consume request-processing capacity.

**[P1] Add idempotency key support for non-idempotent external calls**
Client-generated keys persisted in Postgres with TTL matching retry window. Prevent duplicate operations on retry.

**[P1] Configure correlation header propagation on outbound HTTP**
RestClient/WebClient interceptors auto-inject traceparent, tracestate, and X-Correlation-ID headers.

**[P2] Implement anti-corruption layer for third-party APIs**
Wrap external service clients with dedicated adapter classes translating external errors to internal exception taxonomy.

---

## EPIC 12: Observability Foundation

**[P0] Implement structured JSON logging**
Replace plain-text logs with JSON structured logs containing correlationId, userId (hashed), tenantId, errorCode, severity. Configure logstash-logback-encoder.

**[P0] Add PII and secret scrubbing to log pipeline**
Configure log appenders to mask tokens, credentials, SSNs, credit cards, and secret names. Audit existing logs for leakage.

**[P0] Integrate OpenTelemetry distributed tracing**
Instrument all services. Record exceptions on spans with `span.recordException()`. Propagate context across Temporal, CompletableFuture, SQS boundaries.

**[P1] Add Micrometer metrics for error handling**
Counters by error type/service, timers per dependency, gauges for pool saturation and circuit breaker state, distribution summaries for partial failures.

**[P1] Configure Spring Actuator liveness and readiness probes**
Separate probes. Readiness verifies critical deps (DB, Keycloak, Temporal) but not optional ones (Elasticsearch) supporting graceful degradation.

**[P2] Build error rate SLO dashboards**
Grafana dashboards showing error rate, latency percentiles, circuit breaker state, retry rate per dependency.

---

## EPIC 13: Testing and Chaos Engineering

**[P1] Establish error path test coverage requirements**
Enforce coverage gates specifically on exception branches in service and integration code. Add to CI pipeline.

**[P1] Add Testcontainers integration tests for failure modes**
Test Postgres deadlocks, connection drops, Elasticsearch partial failures, Keycloak outages using realistic containerized dependencies.

**[P1] Implement Temporal TestWorkflowEnvironment test suite**
Validate Saga compensation, retry behavior, timeout handling, and determinism for all workflows.

**[P2] Add LocalStack-based AWS failure testing**
Test S3 slowdown, SQS throttling, KMS failures, Secrets Manager outages using LocalStack fault injection.

**[P2] Implement chaos engineering GameDay runbook**
Periodic exercises killing DB connections, throttling external services, forcing failovers. Validate graceful degradation.

---

## Suggested Labels and Milestones

**Labels to create:** `error-handling`, `security`, `observability`, `resilience`, `tech-debt`, `priority::p0`, `priority::p1`, `priority::p2`, `area::keycloak`, `area::postgres`, `area::elasticsearch`, `area::temporal`, `area::aws`, `area::authz`

**Suggested milestones:** "Error Handling M1: Foundations" (Epics 1-2), "M2: Security Hardening" (Epics 3, 10), "M3: Data Layer Resilience" (Epics 4, 5), "M4: Async and Workflows" (Epics 6-8), "M5: Cloud Integration" (Epics 9, 11), "M6: Operational Excellence" (Epics 12-13)

---

Want me to convert this into a GitLab-importable CSV, generate individual issue templates with acceptance criteria and estimate fields, or produce it as a downloadable document?
