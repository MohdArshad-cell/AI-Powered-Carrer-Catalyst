package com.backend.careercatalyst.dto;

public class TailorRequest {
    // These names MUST match the keys in the JSON payload
    private String resumeText;
    private String jobDescription;

    // Getters and Setters
    public String getResumeText() {
        return resumeText;
    }

    public void setResumeText(String resumeText) {
        this.resumeText = resumeText;
    }

    public String getJobDescription() {
        return jobDescription;
    }

    public void setJobDescription(String jobDescription) {
        this.jobDescription = jobDescription;
    }
}