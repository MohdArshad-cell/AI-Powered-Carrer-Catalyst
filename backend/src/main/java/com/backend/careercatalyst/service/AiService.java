package com.backend.careercatalyst.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.util.ResourceUtils;

import java.io.BufferedReader;
import java.io.File;
import java.io.InputStreamReader;
import java.io.OutputStreamWriter;
import java.nio.charset.StandardCharsets;
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
     * Public method for AI Mock Interview (Question Generator).
     */
    public String getInterviewQuestions(String jobDescription) {
        // We reuse the existing logic but point to the new script
        return runPythonScript("scripts3/interview_generator.py", jobDescription);
    }

    /**
     * Private helper to run Python scripts. This version is corrected to prevent deadlocks.
     */
    private String runPythonScript(String scriptPath, String inputData) {
        Process process = null;
        try {
            File scriptFile = ResourceUtils.getFile("classpath:" + scriptPath);
            String absoluteScriptPath = scriptFile.getAbsolutePath();

            // Using "python" is more portable than a hardcoded path.
            // This relies on python being in the system's PATH.
            ProcessBuilder processBuilder = new ProcessBuilder("python", absoluteScriptPath);
            processBuilder.environment().put("GOOGLE_API_KEY", this.googleApiKey);
            processBuilder.environment().put("PYTHONIOENCODING", "UTF-8");

            process = processBuilder.start();

            // --- CORRECTED LOGIC TO PREVENT DEADLOCK ---

            // STEP 1: Write input to the script and immediately close the stream
            // to signal that you are done sending data.
            try (OutputStreamWriter writer = new OutputStreamWriter(process.getOutputStream(), StandardCharsets.UTF_8)) {
                writer.write(inputData);
            }

            // STEP 2: Read the script's output and error streams BEFORE waiting for it to exit.
            // This clears the I/O buffers and prevents the script from hanging.
            String output = new BufferedReader(new InputStreamReader(process.getInputStream(), StandardCharsets.UTF_8))
                    .lines().collect(Collectors.joining("\n"));

            String errorOutput = new BufferedReader(new InputStreamReader(process.getErrorStream(), StandardCharsets.UTF_8))
                    .lines().collect(Collectors.joining("\n"));

            // STEP 3: NOW, wait for the process to terminate.
            if (!process.waitFor(5, TimeUnit.MINUTES)) {
                process.destroyForcibly();
                throw new RuntimeException("Python script '" + scriptPath + "' execution timed out.");
            }

            // STEP 4: Check the exit code and handle any errors.
            int exitCode = process.exitValue();
            if (exitCode != 0) {
                System.err.println("--- PYTHON SCRIPT ERROR ---");
                System.err.println("SCRIPT: " + scriptPath);
                System.err.println("EXIT CODE: " + exitCode);
                System.err.println("ERROR OUTPUT:\n" + errorOutput);
                System.err.println("--- END PYTHON SCRIPT ERROR ---");
                throw new RuntimeException("Python script exited with a non-zero status. Check console for details.");
            }

            return output;

        } catch (Exception e) {
            // This general exception handling is good to have.
            e.printStackTrace();
            throw new RuntimeException("Error running Python script '" + scriptPath + "'. " + e.getMessage(), e);
        }
    }
}