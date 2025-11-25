package com.backend.careercatalyst.dto;

public class InterviewResponse {
    private String content; // JSON string of questions

    public InterviewResponse(String content) {
        this.content = content;
    }

    public String getContent() { return content; }
    public void setContent(String content) { this.content = content; }
}