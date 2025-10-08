package com.backend.careercatalyst.dto;

public class CoverLetterResponse {
    private String generatedCoverLetter;

    public CoverLetterResponse() {}

    public CoverLetterResponse(String generatedCoverLetter) {
        this.generatedCoverLetter = generatedCoverLetter;
    }

    // Getters and Setters
    public String getGeneratedCoverLetter() {
        return generatedCoverLetter;
    }

    public void setGeneratedCoverLetter(String generatedCoverLetter) {
        this.generatedCoverLetter = generatedCoverLetter;
    }
}