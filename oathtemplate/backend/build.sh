#!/bin/bash

# Build script for keycloak-spring-security-lib
# This script builds the library and optionally the example application

set -e

echo "========================================="
echo "Keycloak Spring Security Library Builder"
echo "========================================="
echo ""

# Function to print colored output
print_green() {
    echo -e "\033[0;32m$1\033[0m"
}

print_yellow() {
    echo -e "\033[0;33m$1\033[0m"
}

print_red() {
    echo -e "\033[0;31m$1\033[0m"
}

# Check if Maven is installed
if ! command -v mvn &> /dev/null; then
    print_red "Error: Maven is not installed or not in PATH"
    exit 1
fi

print_yellow "Maven version:"
mvn -version
echo ""

# Build the library
print_green "Step 1: Building the library..."
echo ""
mvn clean install

if [ $? -eq 0 ]; then
    print_green "✓ Library built successfully!"
    echo ""
    print_yellow "Library installed to local Maven repository:"
    echo "  ~/.m2/repository/com/example/keycloak-spring-security-lib/1.0.0/"
    echo ""
else
    print_red "✗ Library build failed!"
    exit 1
fi

# Ask if user wants to build example
read -p "Do you want to build the example application? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_green "Step 2: Building example application..."
    echo ""
    
    cd examples/basic-app
    mvn clean package
    
    if [ $? -eq 0 ]; then
        print_green "✓ Example application built successfully!"
        echo ""
        print_yellow "Example JAR location:"
        echo "  examples/basic-app/target/example-app-0.0.1-SNAPSHOT.jar"
        echo ""
        print_yellow "To run the example:"
        echo "  cd examples/basic-app"
        echo "  mvn spring-boot:run"
        echo ""
        print_yellow "Don't forget to configure Keycloak settings in:"
        echo "  examples/basic-app/src/main/resources/application.yml"
    else
        print_red "✗ Example application build failed!"
        exit 1
    fi
    
    cd ../..
fi

echo ""
print_green "========================================="
print_green "Build completed successfully!"
print_green "========================================="
echo ""
print_yellow "Next steps:"
echo "  1. Add the library to your project's pom.xml"
echo "  2. Import SecurityConfig and CorsConfig"
echo "  3. Configure Keycloak connection in application.yml"
echo ""
echo "For more information, see:"
echo "  - README.md"
echo "  - INSTALLATION_GUIDE.md"
echo "  - PROJECT_SUMMARY.md"
