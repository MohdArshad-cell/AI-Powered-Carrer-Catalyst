package com.backend.careercatalyst.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;

public class ResumeData {

    @JsonProperty("personal_info")
    private PersonalInfo personalInfo;

    private List<Education> education;

    @JsonProperty("work_experience")
    private List<WorkExperience> workExperience;

    private List<Project> projects;
    private List<SkillItem> skills;
    private List<AchievementItem> achievements;
    private List<CertificationItem> certifications;

    // --- Getters and Setters ---

    public PersonalInfo getPersonalInfo() {
        return personalInfo;
    }

    public void setPersonalInfo(PersonalInfo personalInfo) {
        this.personalInfo = personalInfo;
    }

    public List<Education> getEducation() {
        return education;
    }

    public void setEducation(List<Education> education) {
        this.education = education;
    }

    public List<WorkExperience> getWorkExperience() {
        return workExperience;
    }

    public void setWorkExperience(List<WorkExperience> workExperience) {
        this.workExperience = workExperience;
    }

    public List<Project> getProjects() {
        return projects;
    }

    public void setProjects(List<Project> projects) {
        this.projects = projects;
    }

    public List<SkillItem> getSkills() {
        return skills;
    }

    public void setSkills(List<SkillItem> skills) {
        this.skills = skills;
    }

    public List<AchievementItem> getAchievements() {
        return achievements;
    }

    public void setAchievements(List<AchievementItem> achievements) {
        this.achievements = achievements;
    }

    public List<CertificationItem> getCertifications() {
        return certifications;
    }

    public void setCertifications(List<CertificationItem> certifications) {
        this.certifications = certifications;
    }
}