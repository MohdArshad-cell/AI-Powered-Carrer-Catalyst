package com.backend.careercatalyst.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

public class Education {

    private String degree;
    private String institution;

    @JsonProperty("start_year")
    private String startYear;

    @JsonProperty("end_year")
    private String endYear;

    private String gpa;

    // --- Getters and Setters ---

    public String getDegree() {
        return degree;
    }

    public void setDegree(String degree) {
        this.degree = degree;
    }

    public String getInstitution() {
        return institution;
    }

    public void setInstitution(String institution) {
        this.institution = institution;
    }

    public String getStartYear() {
        return startYear;
    }

    public void setStartYear(String startYear) {
        this.startYear = startYear;
    }

    public String getEndYear() {
        return endYear;
    }

    public void setEndYear(String endYear) {
        this.endYear = endYear;
    }

    public String getGpa() {
        return gpa;
    }

    public void setGpa(String gpa) {
        this.gpa = gpa;
    }
}