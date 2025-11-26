# --- Stage 1: Build the Java Application ---
FROM maven:3.8.5-openjdk-17 AS build
WORKDIR /app
COPY pom.xml .
COPY src ./src
# Build the JAR file
RUN mvn clean package -DskipTests

# --- Stage 2: Create the Runtime Environment ---
FROM eclipse-temurin:17-jdk
WORKDIR /app

# 1. Install Python, Pip, and LaTeX (Required for PDF generation)
# We install 'dos2unix' to fix line ending issues
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    texlive-latex-base \
    texlive-latex-extra \
    texlive-fonts-recommended \
    dos2unix \
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
# 5. Install Dependencies
RUN pip3 install --break-system-packages google-generativeai pdfplumber python-docx python-dotenv pyhumps
RUN pip3 install --break-system-packages -r /app/resume-engine/requirements.txt

# 6. CRITICAL FIX: Convert start.sh to Unix format and make executable
RUN dos2unix /app/start.sh && chmod +x /app/start.sh

# 7. Set Environment Variables
ENV PORT=8080
EXPOSE 8080 8000

# 8. Start Both Services
ENTRYPOINT ["/app/start.sh"]