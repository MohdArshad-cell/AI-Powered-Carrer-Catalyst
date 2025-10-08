package com.backend.careercatalyst.dto;

public class EvaluationResponse {
    private String evaluation;

    public EvaluationResponse() {}
    public EvaluationResponse(String evaluation) { this.evaluation = evaluation; }

    // Getters and Setters
    public String getEvaluation() { return evaluation; }
    public void setEvaluation(String evaluation) { this.evaluation = evaluation; }
}