FROM maven as builder

WORKDIR /app

COPY pom.xml .

RUN mvn dependency:go-offline

COPY src ./src

RUN mvn package -DskipTests

FROM openjdk:21-jre-slim

WORKDIR /app

COPY --from=builder /app/target/hello-docker-app-1.0.0.jar app.jar

CMD ["java", "-jar", "app.jar"]

EXPOSE 8080