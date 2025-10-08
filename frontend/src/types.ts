// src/types.ts

export interface PersonalInfo {
  full_name: string;
  address: string;
  email: string;
  phone: string;
  github_handle: string;
  linkedin_handle: string;
  portfolio_url: string;

}

export interface Education {
  id: string; // Unique ID for mapping
  degree: string;
  institution: string;
  start_year: string;
  end_year: string;
  gpa: string;
}

export interface WorkExperience {
  id: string;
  job_title: string;
  company_name: string;
  location: string;
  start_date: string;
  end_date: string;
  description_points: string; // Will be a single string from textarea
}

export interface Project {
  id: string;
  project_name: string;
  start_date: string;
  end_date: string;
  tech_stack: string;
  description_points: string;
}

export interface Skills {
  languages: string;
  frameworks: string;
  databases: string;
  tools: string;
  cloud_devops: string;
  certifications: string;
}

export interface SkillItem {
  id: string;
  name: string;
  value: string;
}

export interface AchievementItem {
  id: string;
  description: string;
}

export interface CertificationItem {
  id: string;
  name: string;
  issuer: string;
  date: string;
}
export interface ResumeData {
  personal_info: PersonalInfo;
  education: Education[];
  work_experience: WorkExperience[];
  projects: Project[];
  skills: SkillItem[];
  achievements: AchievementItem[];
  certifications: CertificationItem[];
}

export interface DownloadLinks {
  pdfUrl: string;
  latexUrl: string;
  jsonUrl: string;
}