package com.backend.careercatalyst.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

public class GenerateRequest {

    @JsonProperty("template_name")
    private String templateName;

    @JsonProperty("resume_data")
    private ResumeData resumeData;

    // --- Getters and Setters ---

    public String getTemplateName() {
        return templateName;
    }

    public void setTemplateName(String templateName) {
        this.templateName = templateName;
    }

    public ResumeData getResumeData() {
        return resumeData;
    }

    public void setResumeData(ResumeData resumeData) {
        this.resumeData = resumeData;
    }
}