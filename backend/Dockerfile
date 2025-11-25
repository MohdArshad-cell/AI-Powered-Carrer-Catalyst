# --- Stage 1: Build the Java Application ---
FROM maven:3.8.5-openjdk-17 AS build
WORKDIR /app
COPY pom.xml .
COPY src ./src
# Build the JAR file, skipping tests to save time
RUN mvn clean package -DskipTests

# --- Stage 2: Create the Runtime Environment ---
FROM eclipse-temurin:17-jdk
WORKDIR /app

# 1. Install Python, Pip, and LaTeX (Required for PDF generation)
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    texlive-latex-base \
    texlive-latex-extra \
    texlive-fonts-recommended \
    && rm -rf /var/lib/apt/lists/*

# 2. Copy the built JAR file
COPY --from=build /app/target/*.jar app.jar

# 3. Copy AI Scripts
COPY src/main/resources/scripts /app/scripts
COPY src/main/resources/scripts1 /app/scripts1
COPY src/main/resources/scripts2 /app/scripts2
COPY src/main/resources/scripts3 /app/scripts3

# 4. Copy the Resume Engine & Startup Script
COPY resume-engine /app/resume-engine
COPY start.sh /app/start.sh

# 5. Install Dependencies
# Install AI Script dependencies
RUN pip3 install --break-system-packages google-generativeai pdfplumber python-docx python-dotenv

# Install Resume Engine dependencies
RUN pip3 install --break-system-packages -r /app/resume-engine/requirements.txt

# 6. Permissions & Env
RUN chmod +x /app/start.sh
ENV PORT=8080
EXPOSE 8080 8000

# 7. Start Both Services
ENTRYPOINT ["/app/start.sh"]