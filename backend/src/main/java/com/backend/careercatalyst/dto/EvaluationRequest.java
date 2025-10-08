package com.backend.careercatalyst.dto;

public class EvaluationRequest {
    private String resume;
    private String jobDescription;

    // Getters and Setters
    public String getResume() { return resume; }
    public void setResume(String resume) { this.resume = resume; }
    public String getJobDescription() { return jobDescription; }
    public void setJobDescription(String jobDescription) { this.jobDescription = jobDescription; }
}