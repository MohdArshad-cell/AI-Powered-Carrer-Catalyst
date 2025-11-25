package com.backend.careercatalyst.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Service;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.StandardCopyOption;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;

@Service
public class AiService {

    @Value("${google.api.key}")
    private String googleApiKey;

    /**
     * Public method for the AI Resume Tailor.
     */
    public String getTailoredResume(String resume, String jobDescription) {
        String combinedInput = (resume != null ? resume : "") + "\n---DELIMITER---\n" + (jobDescription != null ? jobDescription : "");
        return runPythonScript("scripts/tailor.py", combinedInput);
    }

    /**
     * Public method for the ATS Evaluator.
     */
    public String getEvaluationResult(String resume, String jobDescription) {
        String combinedInput = (resume != null ? resume : "") + "\n---DELIMITER---\n" + (jobDescription != null ? jobDescription : "");
        return runPythonScript("scripts1/evaluate.py", combinedInput);
    }

    /**
     * Public method for the AI Cover Letter Generator.
     */
    public String getGeneratedCoverLetter(String resume, String jobDescription) {
        String combinedInput = (resume != null ? resume : "") + "\n---DELIMITER---\n" + (jobDescription != null ? jobDescription : "");
        return runPythonScript("scripts2/coverletter.py", combinedInput);
    }

    /**
     * Public method for Bulk Resume Scoring.
     */
    public String bulkScanResumes(String directoryPath, String jobDescription) {
        return runPythonScriptWithArgs("scripts/bulk_score.py", directoryPath, jobDescription);
    }

    /**
     * Public method for AI Mock Interview (Question Generator).
     */
    public String getInterviewQuestions(String jobDescription) {
        return runPythonScript("scripts3/interview_generator.py", jobDescription);
    }

    /**
     * Helper to copy a script from the JAR to a temporary file so Python can run it.
     */
    private File copyScriptToTempFile(String scriptPath) throws IOException {
        // 1. Load the file from the JAR (Classpath)
        ClassPathResource resource = new ClassPathResource(scriptPath);
        if (!resource.exists()) {
            throw new FileNotFoundException("Script not found in JAR: " + scriptPath);
        }

        // 2. Create a temp file
        String extension = scriptPath.contains(".") ? scriptPath.substring(scriptPath.lastIndexOf(".")) : ".tmp";
        File tempFile = File.createTempFile("ai_script_", extension);
        tempFile.deleteOnExit(); // Auto-delete when app stops

        // 3. Copy the content
        try (InputStream inputStream = resource.getInputStream()) {
            Files.copy(inputStream, tempFile.toPath(), StandardCopyOption.REPLACE_EXISTING);
        }
        
        // 4. Also copy helper text files if needed (like prompt templates) in the same directory
        // This is a bit tricky in JARs. For now, we assume prompts are handled by the python script loading or 
        // we just ensure the python script is self-contained. 
        // *If your python scripts load other .txt files using relative paths, 
        // *you might need to update the python scripts to load those from strings passed by Java instead.
        // *However, for this fix, we focus on running the main script.

        return tempFile;
    }

    /**
     * Runs a Python script using STDIN for input (Tailor, ATS, Cover Letter, Interview).
     */
    private String runPythonScript(String scriptPath, String inputData) {
        Process process = null;
        try {
            // FIX: Extract file from JAR to Temp
            File scriptFile = copyScriptToTempFile(scriptPath);

            // Use "python3" for Linux/Docker environments
            ProcessBuilder processBuilder = new ProcessBuilder("python3", scriptFile.getAbsolutePath());
            processBuilder.environment().put("GOOGLE_API_KEY", this.googleApiKey);
            processBuilder.environment().put("PYTHONIOENCODING", "UTF-8");

            process = processBuilder.start();

            try (OutputStreamWriter writer = new OutputStreamWriter(process.getOutputStream(), StandardCharsets.UTF_8)) {
                writer.write(inputData);
            }

            String output = new BufferedReader(new InputStreamReader(process.getInputStream(), StandardCharsets.UTF_8))
                    .lines().collect(Collectors.joining("\n"));

            String errorOutput = new BufferedReader(new InputStreamReader(process.getErrorStream(), StandardCharsets.UTF_8))
                    .lines().collect(Collectors.joining("\n"));

            if (!process.waitFor(2, TimeUnit.MINUTES)) {
                process.destroyForcibly();
                throw new RuntimeException("Python script '" + scriptPath + "' execution timed out.");
            }

            if (process.exitValue() != 0) {
                System.err.println("--- PYTHON ERROR ---");
                System.err.println("Script: " + scriptPath);
                System.err.println("Error: " + errorOutput);
                throw new RuntimeException("Python script failed: " + errorOutput);
            }

            return output;

        } catch (Exception e) {
            e.printStackTrace();
            throw new RuntimeException("Error running Python script: " + e.getMessage(), e);
        }
    }

    /**
     * Runs a Python script using Arguments (Bulk Scan).
     */
    private String runPythonScriptWithArgs(String scriptPath, String... args) {
        try {
            // FIX: Extract file from JAR to Temp
            File scriptFile = copyScriptToTempFile(scriptPath);

            List<String> command = new ArrayList<>();
            command.add("python3");
            command.add(scriptFile.getAbsolutePath());
            Collections.addAll(command, args);

            ProcessBuilder processBuilder = new ProcessBuilder(command);
            processBuilder.environment().put("GOOGLE_API_KEY", this.googleApiKey);
            processBuilder.environment().put("PYTHONIOENCODING", "UTF-8");

            Process process = processBuilder.start();

            String output = new BufferedReader(new InputStreamReader(process.getInputStream(), StandardCharsets.UTF_8))
                    .lines().collect(Collectors.joining("\n"));

            String errorOutput = new BufferedReader(new InputStreamReader(process.getErrorStream(), StandardCharsets.UTF_8))
                    .lines().collect(Collectors.joining("\n"));

            if (!process.waitFor(5, TimeUnit.MINUTES)) {
                process.destroyForcibly();
                throw new RuntimeException("Script execution timed out.");
            }

            if (process.exitValue() != 0) {
                System.err.println("PYTHON ERROR: " + errorOutput);
                throw new RuntimeException("Python script failed. Check logs.");
            }

            return output;

        } catch (Exception e) {
            e.printStackTrace();
            throw new RuntimeException("Error running script: " + e.getMessage());
        }
    }
}