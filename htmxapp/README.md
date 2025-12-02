<pre>
spring-htmx-app/
├── docker-compose.yml          # Docker orchestration
├── Dockerfile                  # Spring Boot container
├── pom.xml                     # Maven dependencies
├── src/main/
│   ├── java/com/example/taskapp/
│   │   ├── TaskApplication.java       # Main application
│   │   ├── model/Task.java           # Task entity with ID, name, task
│   │   ├── repository/TaskRepository.java
│   │   └── controller/TaskController.java  # CRUD endpoints
│   └── resources/
│       ├── application.properties    # Database config
│       └── templates/
│           ├── index.html           # Main page
│           └── fragments/
│               ├── task-list.html   # Task list component
│               └── task-form.html   # Edit form component
</pre>