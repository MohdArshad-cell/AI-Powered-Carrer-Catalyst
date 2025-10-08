package com.backend.careercatalyst.dto;

public class TailorResponse {
    private String tailoredResume;

    public TailorResponse(String tailoredResume) {
        this.tailoredResume = tailoredResume;
    }

    // Getter and Setter
    public String getTailoredResume() {
        return tailoredResume;
    }

    public void setTailoredResume(String tailoredResume) {
        this.tailoredResume = tailoredResume;
    }
}