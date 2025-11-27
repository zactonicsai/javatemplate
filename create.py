import requests
import zipfile
import io
import os
import argparse
import textwrap
import stat

# --- Configuration ---
INITIALIZR_URL = "https://start.spring.io/starter.zip"

def generate_and_extract_spring_boot_project(url, params, output_dir):
    """
    Makes an API request to Spring Initializr, downloads the ZIP, and extracts it.
    """
    print(f"🚀 Requesting project from {url}...")
    print(f"   - Project Name: {params.get('name')}")
    print(f"   - Java Version: {params.get('javaVersion')}")
    print(f"   - Dependencies: {params.get('dependencies')}")
    print(f"   - Build Tool: {params.get('type')}")
    
    try:
        # Make the GET request
        response = requests.get(url, params=params)
        
        # Check if the request was successful (HTTP status code 200)
        if response.status_code == 200:
            print("✅ Successfully downloaded project ZIP.")
            
            # Use io.BytesIO to treat the response content as a file in memory
            zip_file = zipfile.ZipFile(io.BytesIO(response.content))
            
            # Create the destination directory if it doesn't exist
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # Extract the contents to the destination directory
            zip_file.extractall(output_dir)
            print(f"📂 Project extracted successfully to: **{output_dir}**") 
            
            return True
            
        else:
            print(f"❌ Failed to download project. HTTP Status Code: {response.status_code}")
            print("Error Details:\n", response.text)
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ An error occurred during the HTTP request: {e}")
        return False

def make_wrapper_executable(output_dir, build_type):
    """
    Make Maven/Gradle wrapper executable on Unix systems.
    """
    if build_type == 'maven-project':
        wrapper_path = os.path.join(output_dir, 'mvnw')
    else:
        wrapper_path = os.path.join(output_dir, 'gradlew')
    
    if os.path.exists(wrapper_path):
        try:
            # Add execute permission
            st = os.stat(wrapper_path)
            os.chmod(wrapper_path, st.st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)
            print(f"✅ Made {os.path.basename(wrapper_path)} executable")
        except Exception as e:
            print(f"⚠️  Warning: Could not make wrapper executable: {e}")

def verify_pom_xml(output_dir):
    """
    Verify and fix pom.xml to ensure Spring Boot plugin is properly configured.
    """
    pom_path = os.path.join(output_dir, 'pom.xml')
    
    if not os.path.exists(pom_path):
        print("⚠️  Warning: pom.xml not found")
        return False
    
    with open(pom_path, 'r') as f:
        content = f.read()
    
    # Check if Spring Boot plugin exists
    if 'spring-boot-maven-plugin' not in content:
        print("⚠️  Warning: Spring Boot Maven Plugin not found in pom.xml")
        
        # Add the plugin
        plugin_section = textwrap.dedent('''\
            \t<build>
            \t\t<plugins>
            \t\t\t<plugin>
            \t\t\t\t<groupId>org.springframework.boot</groupId>
            \t\t\t\t<artifactId>spring-boot-maven-plugin</artifactId>
            \t\t\t</plugin>
            \t\t</plugins>
            \t</build>
        ''')
        
        # Insert before </project>
        content = content.replace('</project>', f'{plugin_section}\n</project>')
        
        with open(pom_path, 'w') as f:
            f.write(content)
        
        print("✅ Added Spring Boot Maven Plugin to pom.xml")
    
    return True

def find_source_directory(output_dir, package_name):
    """
    Find the source directory based on package name.
    """
    # Convert package name to directory path (e.g., com.example.demo -> com/example/demo)
    package_path = package_name.replace('.', '/')
    
    # Typical Maven/Gradle structure
    source_path = os.path.join(output_dir, 'src', 'main', 'java', package_path)
    
    if os.path.exists(source_path):
        return source_path
    else:
        print(f"⚠️  Warning: Could not find source directory at {source_path}")
        return None

def create_hello_controller(source_dir, package_name):
    """
    Create a HelloController with a simple REST endpoint.
    """
    controller_content = textwrap.dedent(f'''\
        package {package_name};

        import org.springframework.web.bind.annotation.GetMapping;
        import org.springframework.web.bind.annotation.RequestParam;
        import org.springframework.web.bind.annotation.RestController;

        @RestController
        public class HelloController {{

            @GetMapping("/hello")
            public String hello(@RequestParam(value = "name", defaultValue = "World") String name) {{
                return String.format("Hello, %s! 👋", name);
            }}

            @GetMapping("/api/greet")
            public GreetingResponse greet(@RequestParam(value = "name", defaultValue = "Guest") String name) {{
                return new GreetingResponse(
                    String.format("Hello, %s!", name),
                    System.currentTimeMillis()
                );
            }}

            // Simple response class
            record GreetingResponse(String message, long timestamp) {{}}
        }}
    ''')
    
    controller_path = os.path.join(source_dir, 'HelloController.java')
    
    try:
        with open(controller_path, 'w') as f:
            f.write(controller_content)
        print(f"✅ Created HelloController at: {controller_path}")
        return True
    except Exception as e:
        print(f"❌ Failed to create HelloController: {e}")
        return False

def create_home_controller(source_dir, package_name, project_name):
    """
    Create a HomeController that returns an HTML template.
    """
    controller_content = textwrap.dedent(f'''\
        package {package_name};

        import org.springframework.stereotype.Controller;
        import org.springframework.ui.Model;
        import org.springframework.web.bind.annotation.GetMapping;
        import org.springframework.web.bind.annotation.ResponseBody;

        import java.time.LocalDateTime;
        import java.time.format.DateTimeFormatter;

        @Controller
        public class HomeController {{

            @GetMapping("/")
            public String home(Model model) {{
                model.addAttribute("projectName", "{project_name}");
                model.addAttribute("message", "Auto-generated template");
                model.addAttribute("timestamp", LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")));
                return "home";
            }}

            @GetMapping("/api/info")
            @ResponseBody
            public ProjectInfo info() {{
                return new ProjectInfo(
                    "{project_name}",
                    "Auto-generated template",
                    LocalDateTime.now().toString()
                );
            }}

            // Simple response class for API
            record ProjectInfo(String name, String description, String timestamp) {{}}
        }}
    ''')
    
    controller_path = os.path.join(source_dir, 'HomeController.java')
    
    try:
        with open(controller_path, 'w') as f:
            f.write(controller_content)
        print(f"✅ Created HomeController at: {controller_path}")
        return True
    except Exception as e:
        print(f"❌ Failed to create HomeController: {e}")
        return False

def create_home_template(output_dir, project_name):
    """
    Create a simple Thymeleaf HTML template for the home page.
    """
    # Create templates directory
    templates_dir = os.path.join(output_dir, 'src', 'main', 'resources', 'templates')
    
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
    
    template_content = textwrap.dedent(f'''\
        <!DOCTYPE html>
        <html xmlns:th="http://www.thymeleaf.org">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title th:text="${{projectName}}">Spring Boot App</title>
            <style>
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    padding: 20px;
                }}
                
                .container {{
                    background: white;
                    border-radius: 20px;
                    padding: 60px 40px;
                    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                    text-align: center;
                    max-width: 600px;
                    width: 100%;
                }}
                
                h1 {{
                    color: #333;
                    font-size: 2.5em;
                    margin-bottom: 20px;
                    font-weight: 700;
                }}
                
                .badge {{
                    display: inline-block;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 8px 20px;
                    border-radius: 20px;
                    font-size: 0.9em;
                    margin-bottom: 30px;
                    font-weight: 600;
                }}
                
                .message {{
                    color: #666;
                    font-size: 1.2em;
                    margin-bottom: 40px;
                    line-height: 1.6;
                }}
                
                .info-box {{
                    background: #f8f9fa;
                    border-radius: 10px;
                    padding: 20px;
                    margin-bottom: 30px;
                }}
                
                .info-item {{
                    display: flex;
                    justify-content: space-between;
                    padding: 10px 0;
                    border-bottom: 1px solid #e0e0e0;
                }}
                
                .info-item:last-child {{
                    border-bottom: none;
                }}
                
                .info-label {{
                    font-weight: 600;
                    color: #555;
                }}
                
                .info-value {{
                    color: #667eea;
                    font-weight: 500;
                }}
                
                .endpoints {{
                    text-align: left;
                    margin-top: 30px;
                }}
                
                .endpoints h3 {{
                    color: #333;
                    margin-bottom: 15px;
                    font-size: 1.3em;
                }}
                
                .endpoint {{
                    background: #f8f9fa;
                    border-left: 4px solid #667eea;
                    padding: 12px 15px;
                    margin-bottom: 10px;
                    border-radius: 4px;
                    font-family: 'Courier New', monospace;
                    font-size: 0.9em;
                }}
                
                .endpoint code {{
                    color: #667eea;
                    font-weight: 600;
                }}
                
                .footer {{
                    margin-top: 40px;
                    color: #999;
                    font-size: 0.85em;
                }}
                
                .emoji {{
                    font-size: 3em;
                    margin-bottom: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="emoji">🚀</div>
                <h1 th:text="${{projectName}}">{project_name}</h1>
                <div class="badge" th:text="${{message}}">Auto-generated template</div>
                
                <div class="message">
                    Welcome to your new Spring Boot application! This template was automatically 
                    generated and is ready for development.
                </div>
                
                <div class="info-box">
                    <div class="info-item">
                        <span class="info-label">Status</span>
                        <span class="info-value">✅ Running</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Generated</span>
                        <span class="info-value" th:text="${{timestamp}}">2024-01-01</span>
                    </div>
                </div>
                
                <div class="endpoints">
                    <h3>📍 Available Endpoints</h3>
                    <div class="endpoint">
                        <code>GET /</code> - This home page
                    </div>
                    <div class="endpoint">
                        <code>GET /hello?name=YourName</code> - Simple greeting
                    </div>
                    <div class="endpoint">
                        <code>GET /api/greet?name=YourName</code> - JSON greeting response
                    </div>
                    <div class="endpoint">
                        <code>GET /api/info</code> - Project information (JSON)
                    </div>
                </div>
                
                <div class="footer">
                    <p>Powered by Spring Boot 🍃</p>
                </div>
            </div>
        </body>
        </html>
    ''')
    
    template_path = os.path.join(templates_dir, 'home.html')
    
    try:
        with open(template_path, 'w') as f:
            f.write(template_content)
        print(f"✅ Created home.html template at: {template_path}")
        return True
    except Exception as e:
        print(f"❌ Failed to create home template: {e}")
        return False

def update_dependencies_for_thymeleaf(output_dir, build_type):
    """
    Add Thymeleaf dependency to pom.xml or build.gradle if not present.
    """
    if build_type == 'maven-project':
        pom_path = os.path.join(output_dir, 'pom.xml')
        
        if os.path.exists(pom_path):
            with open(pom_path, 'r') as f:
                content = f.read()
            
            # Check if Thymeleaf is already present
            if 'spring-boot-starter-thymeleaf' not in content:
                # Find the dependencies section and add Thymeleaf
                thymeleaf_dep = textwrap.dedent('''\
                \t\t<dependency>
                \t\t\t<groupId>org.springframework.boot</groupId>
                \t\t\t<artifactId>spring-boot-starter-thymeleaf</artifactId>
                \t\t</dependency>
                ''')
                
                # Insert before </dependencies>
                content = content.replace('</dependencies>', f'{thymeleaf_dep}\t</dependencies>')
                
                with open(pom_path, 'w') as f:
                    f.write(content)
                
                print("✅ Added Thymeleaf dependency to pom.xml")
            else:
                print("ℹ️  Thymeleaf dependency already present in pom.xml")
    
    elif 'gradle' in build_type:
        build_gradle_path = os.path.join(output_dir, 'build.gradle')
        
        if os.path.exists(build_gradle_path):
            with open(build_gradle_path, 'r') as f:
                content = f.read()
            
            if 'spring-boot-starter-thymeleaf' not in content:
                # Add Thymeleaf dependency
                thymeleaf_dep = "\timplementation 'org.springframework.boot:spring-boot-starter-thymeleaf'\n"
                
                # Find dependencies block and add
                if 'dependencies {' in content:
                    content = content.replace('dependencies {', f'dependencies {{\n{thymeleaf_dep}')
                    
                    with open(build_gradle_path, 'w') as f:
                        f.write(content)
                    
                    print("✅ Added Thymeleaf dependency to build.gradle")
            else:
                print("ℹ️  Thymeleaf dependency already present in build.gradle")

def parse_arguments():
    """
    Parse command-line arguments for Spring Boot project generation.
    """
    parser = argparse.ArgumentParser(
        description='Generate a Spring Boot project with auto-generated controllers',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Basic usage with defaults
  python %(prog)s
  
  # Custom project name
  python %(prog)s --name MyRestAPI --java-version 17
  
  # Skip controller generation
  python %(prog)s --name MyApp --no-controllers
  
  # Full customization
  python %(prog)s --name MyService --group-id org.mycompany --java-version 21
        '''
    )
    
    # Project identification
    parser.add_argument('--name', 
                        default='Java21WebLombokApp',
                        help='Project name (default: Java21WebLombokApp)')
    
    parser.add_argument('--group-id', 
                        default='com.example',
                        help='Group ID for the project (default: com.example)')
    
    parser.add_argument('--artifact-id', 
                        help='Artifact ID (default: lowercase project name)')
    
    parser.add_argument('--package-name',
                        help='Base package name (default: groupId.artifactId)')
    
    parser.add_argument('--description',
                        help='Project description (default: auto-generated)')
    
    # Build configuration
    parser.add_argument('--type',
                        choices=['maven-project', 'gradle-project', 'gradle-project-kotlin'],
                        default='maven-project',
                        help='Project build tool (default: maven-project)')
    
    parser.add_argument('--language',
                        choices=['java', 'kotlin', 'groovy'],
                        default='java',
                        help='Programming language (default: java)')
    
    parser.add_argument('--java-version',
                        choices=['17', '21', '23'],
                        default='21',
                        help='Java version (default: 21)')
    
    parser.add_argument('--boot-version',
                        help='Spring Boot version (default: latest stable)')
    
    # Dependencies
    parser.add_argument('--dependencies',
                        default='web,lombok',
                        help='Comma-separated list of dependencies (default: web,lombok)')
    
    # Output configuration
    parser.add_argument('--output-dir',
                        help='Output directory (default: ./ProjectName)')
    
    parser.add_argument('--url',
                        default=INITIALIZR_URL,
                        help=f'Spring Initializr URL (default: {INITIALIZR_URL})')
    
    # Controller generation options
    parser.add_argument('--no-controllers',
                        action='store_true',
                        help='Skip automatic controller generation')
    
    return parser.parse_args()

def build_params(args):
    """
    Build the parameters dictionary from command-line arguments.
    """
    # Use artifact-id if provided, otherwise use lowercase project name
    artifact_id = args.artifact_id if args.artifact_id else args.name.lower()
    
    # Use package-name if provided, otherwise construct from group-id and artifact-id
    package_name = args.package_name if args.package_name else f"{args.group_id}.{artifact_id.replace('-', '')}"
    
    # Use description if provided, otherwise auto-generate
    description = args.description if args.description else f"Spring Boot project: {args.name}"
    
    params = {
        'type': args.type,
        'language': args.language,
        'groupId': args.group_id,
        'artifactId': artifact_id,
        'name': args.name,
        'description': description,
        'packageName': package_name,
        'javaVersion': args.java_version,
        'dependencies': args.dependencies
    }
    
    # Add bootVersion only if specified
    if args.boot_version:
        params['bootVersion'] = args.boot_version
    
    return params

def print_troubleshooting_guide(output_dir, build_type):
    """
    Print troubleshooting guide if there are issues.
    """
    print("\n" + "="*60)
    print("🔧 TROUBLESHOOTING GUIDE")
    print("="*60)
    
    if build_type == 'maven-project':
        print("\nIf you encounter Maven errors, try these steps:\n")
        print("1. Verify Java is installed:")
        print("   java -version")
        print("\n2. Try running with the full command:")
        print(f"   cd {output_dir}")
        print("   ./mvnw clean spring-boot:run")
        print("\n3. If mvnw is not executable:")
        print("   chmod +x mvnw")
        print("   ./mvnw clean spring-boot:run")
        print("\n4. On Windows, use:")
        print("   mvnw.cmd spring-boot:run")
        print("\n5. If still having issues, compile first:")
        print("   ./mvnw clean install")
        print("   ./mvnw spring-boot:run")
        print("\n6. Alternative: Use IDE")
        print("   - Open project in IntelliJ/Eclipse/VS Code")
        print("   - Run the main Application class")
    else:
        print("\nIf you encounter Gradle errors, try these steps:\n")
        print("1. Verify Java is installed:")
        print("   java -version")
        print("\n2. Try running with the full command:")
        print(f"   cd {output_dir}")
        print("   ./gradlew clean bootRun")
        print("\n3. If gradlew is not executable:")
        print("   chmod +x gradlew")
        print("   ./gradlew bootRun")
        print("\n4. On Windows, use:")
        print("   gradlew.bat bootRun")
    
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    # Parse command-line arguments
    args = parse_arguments()
    
    # Build parameters dictionary
    params = build_params(args)
    
    # Determine output directory
    output_dir = args.output_dir if args.output_dir else f"./{args.name}"
    
    # Generate and extract the project
    success = generate_and_extract_spring_boot_project(args.url, params, output_dir)
    
    if success:
        # Make wrapper executable
        make_wrapper_executable(output_dir, params['type'])
        
        # Verify and fix pom.xml for Maven projects
        if params['type'] == 'maven-project':
            verify_pom_xml(output_dir)
        
        if not args.no_controllers:
            print("\n📝 Adding controllers to project...")
            
            # Find the source directory
            package_name = params['packageName']
            source_dir = find_source_directory(output_dir, package_name)
            
            if source_dir:
                # Create controllers
                create_hello_controller(source_dir, package_name)
                create_home_controller(source_dir, package_name, params['name'])
                
                # Create home template
                create_home_template(output_dir, params['name'])
                
                # Update dependencies to include Thymeleaf
                update_dependencies_for_thymeleaf(output_dir, params['type'])
                
                print("\n✨ Project setup complete!")
                print(f"\n📋 Next steps:")
                print(f"   1. cd {output_dir}")
                
                if params['type'] == 'maven-project':
                    print(f"   2. ./mvnw clean spring-boot:run")
                else:
                    print(f"   2. ./gradlew clean bootRun")
                
                print(f"   3. Open http://localhost:8080 in your browser")
                print(f"\n🌐 Available endpoints:")
                print(f"   • http://localhost:8080/         - Home page")
                print(f"   • http://localhost:8080/hello    - Hello endpoint")
                print(f"   • http://localhost:8080/api/greet - Greeting API")
                print(f"   • http://localhost:8080/api/info  - Project info API")
                
                # Print troubleshooting guide
                print_troubleshooting_guide(output_dir, params['type'])
            else:
                print("\n⚠️  Could not find source directory. Controllers not created.")
        else:
            print("\n✨ Project created successfully (controllers skipped)")
            print(f"\n📋 Next steps:")
            print(f"   1. cd {output_dir}")
            
            if params['type'] == 'maven-project':
                print(f"   2. ./mvnw spring-boot:run")
            else:
                print(f"   2. ./gradlew bootRun")
            
            print_troubleshooting_guide(output_dir, params['type'])