FROM maven as builder

WORKDIR /app

COPY pom.xml .

RUN mvn dependency:go-offline

COPY src ./src

RUN mvn package -DskipTests

FROM openjdk:26-ea-jdk

WORKDIR /app

COPY --from=builder /app/target/htmxapp-v1.jar app.jar

CMD ["java", "-jar", "app.jar"]

EXPOSE 8080