# --- Stage 1: Build the Java Application ---
FROM maven:3.8.5-openjdk-17 AS build
WORKDIR /app
COPY pom.xml .
COPY src ./src
# Build the JAR file, skipping tests to save time
RUN mvn clean package -DskipTests

# --- Stage 2: Create the Runtime Environment (Java + Python) ---
# FIX: Switched from 'openjdk:17-jdk-slim' to 'eclipse-temurin:17-jdk'
FROM eclipse-temurin:17-jdk
WORKDIR /app

# 1. Install Python and Pip (Eclipse Temurin is Ubuntu-based, so apt-get works)
RUN apt-get update && apt-get install -y python3 python3-pip

# 2. Copy the built JAR file from Stage 1
COPY --from=build /app/target/*.jar app.jar

# 3. Copy your Python scripts and requirements
COPY src/main/resources/scripts /app/scripts
COPY src/main/resources/scripts1 /app/scripts1
COPY src/main/resources/scripts2 /app/scripts2
COPY src/main/resources/scripts3 /app/scripts3

# 4. Install Python Dependencies
# Combine requirements installation to ensure all libs are present
RUN pip3 install -r /app/scripts/requirements.txt || true
RUN pip3 install google-generativeai pdfplumber python-docx

# 5. Set Environment Variables
ENV PORT=8080
EXPOSE 8080

# 6. Run the Application
ENTRYPOINT ["java", "-jar", "app.jar"]