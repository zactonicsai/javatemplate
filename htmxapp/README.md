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

# Spring Boot HTMX Task Manager

A modern task management application built with:
- **Java 21**
- **Spring Boot 3.4.0**
- **HTMX** for dynamic interactions
- **Tailwind CSS** for styling
- **PostgreSQL** database
- **Docker Compose** for easy deployment

## Features

✅ Create, Read, Update, Delete (CRUD) operations for tasks
✅ Real-time updates without page refresh using HTMX
✅ Beautiful UI with Tailwind CSS
✅ PostgreSQL database for data persistence
✅ Docker containerization
✅ Form validation

## Prerequisites

- Docker and Docker Compose installed on your system

## Getting Started

### 1. Clone or navigate to the project directory

```bash
cd spring-htmx-app
```

### 2. Build and run with Docker Compose

```bash
docker-compose up --build
```

This command will:
- Build the Spring Boot application
- Start PostgreSQL database
- Run the application on port 8080

### 3. Access the application

Open your browser and navigate to:
```
http://localhost:8080
```

## Architecture

### Project Structure
```
spring-htmx-app/
├── src/
│   └── main/
│       ├── java/
│       │   └── com/example/taskapp/
│       │       ├── TaskApplication.java
│       │       ├── controller/
│       │       │   └── TaskController.java
│       │       ├── model/
│       │       │   └── Task.java
│       │       └── repository/
│       │           └── TaskRepository.java
│       └── resources/
│           ├── application.properties
│           └── templates/
│               ├── index.html
│               └── fragments/
│                   ├── task-list.html
│                   └── task-form.html
├── Dockerfile
├── docker-compose.yml
└── pom.xml
```

### Key Components

**Task Entity**
- `id` (Long): Auto-generated unique identifier
- `name` (String): Name of the person
- `task` (String): Task description

**HTMX Integration**
- Uses `hx-post`, `hx-put`, `hx-delete`, `hx-get` for AJAX requests
- Dynamic content updates without full page reload
- Smooth transitions and user experience

**Tailwind CSS**
- Modern, responsive design
- Gradient backgrounds
- Interactive hover effects
- Clean form styling

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Main page with task list and form |
| POST | `/tasks` | Create a new task |
| GET | `/tasks/{id}/edit` | Get edit form for a task |
| PUT | `/tasks/{id}` | Update an existing task |
| DELETE | `/tasks/{id}` | Delete a task |
| GET | `/tasks/{id}/cancel` | Cancel edit mode |

## Database Configuration

The PostgreSQL database is configured with:
- Database: `taskdb`
- Username: `taskuser`
- Password: `taskpass`
- Port: `5432`

## Development

### Running without Docker

If you want to run locally without Docker:

1. Start PostgreSQL on your local machine
2. Update `application.properties` with your database credentials
3. Run:
```bash
mvn spring-boot:run
```

### Stopping the Application

```bash
docker-compose down
```

To remove volumes as well:
```bash
docker-compose down -v
```

## Technologies Used

- **Spring Boot 3.5.8**: Modern Java framework
- **Java 21**: Latest LTS version with modern features
- **HTMX 1.9.10**: High-power tools for HTML
- **Tailwind CSS**: Utility-first CSS framework
- **PostgreSQL 16**: Robust relational database
- **Thymeleaf**: Server-side Java template engine
- **Spring Data JPA**: Data access layer
- **Lombok**: Reduce boilerplate code
- **Maven**: Build and dependency management

## License

MIT License - Feel free to use this project for learning and development!