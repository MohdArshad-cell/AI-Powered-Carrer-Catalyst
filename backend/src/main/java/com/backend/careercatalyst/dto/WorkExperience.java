package com.backend.careercatalyst.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;

public class WorkExperience {

    @JsonProperty("job_title")
    private String jobTitle;

    @JsonProperty("company_name")
    private String companyName;

    private String location;

    @JsonProperty("start_date")
    private String startDate;

    @JsonProperty("end_date")
    private String endDate;

    @JsonProperty("description_points")
    private List<String> descriptionPoints;

    // --- Getters and Setters ---

    public String getJobTitle() {
        return jobTitle;
    }

    public void setJobTitle(String jobTitle) {
        this.jobTitle = jobTitle;
    }

    public String getCompanyName() {
        return companyName;
    }

    public void setCompanyName(String companyName) {
        this.companyName = companyName;
    }

    public String getLocation() {
        return location;
    }

    public void setLocation(String location) {
        this.location = location;
    }

    public String getStartDate() {
        return startDate;
    }

    public void setStartDate(String startDate) {
        this.startDate = startDate;
    }

    public String getEndDate() {
        return endDate;
    }

    public void setEndDate(String endDate) {
        this.endDate = endDate;
    }

    public List<String> getDescriptionPoints() {
        return descriptionPoints;
    }

    public void setDescriptionPoints(List<String> descriptionPoints) {
        this.descriptionPoints = descriptionPoints;
    }
}