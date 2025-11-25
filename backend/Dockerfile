# --- Stage 1: Build the Java Application ---
FROM maven:3.8.5-openjdk-17 AS build
WORKDIR /app

COPY pom.xml .
COPY src ./src

RUN mvn clean package -DskipTests

# --- Stage 2: Runtime Environment (Java + Python) ---
FROM eclipse-temurin:17-jdk
WORKDIR /app

# 1. Install Python and Dependencies
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 2. Copy JAR
COPY --from=build /app/target/*.jar app.jar

# 3. Copy Python Scripts
COPY src/main/resources/scripts  /app/scripts
COPY src/main/resources/scripts1 /app/scripts1
COPY src/main/resources/scripts2 /app/scripts2
COPY src/main/resources/scripts3 /app/scripts3

# 4. Install Python Requirements

RUN pip3 install --break-system-packages google-generativeai pdfplumber python-docx

# 5. Environment
ENV PORT=8080
EXPOSE 8080

# 6. Start App
ENTRYPOINT ["java", "-jar", "app.jar"]
