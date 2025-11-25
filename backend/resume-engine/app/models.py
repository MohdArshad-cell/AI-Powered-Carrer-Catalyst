from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from humps import camelize

# Helper function to convert snake_case to camelCase for the API schema
def to_camel(string):
    return camelize(string)

# Base model with the camelCase configuration
class CamelCaseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

# --- All your models now inherit from CamelCaseModel ---

class PersonalInfo(CamelCaseModel):
    full_name: str
    address: str
    email: str
    phone: str
    github_handle: Optional[str] = None
    linkedin_handle: Optional[str] = None
    portfolio_url: Optional[str] = None
    extra_info: Optional[str] = None

class Education(CamelCaseModel):
    degree: str
    institution: str
    start_year: str
    end_year: str
    gpa: Optional[str] = None

class WorkExperience(CamelCaseModel):
    job_title: str
    company_name: str
    location: str
    start_date: str
    end_date: str
    description_points: List[str]

class Project(CamelCaseModel):
    project_name: str
    start_date: str
    end_date: str
    tech_stack: str
    description_points: List[str]

class SkillItem(CamelCaseModel):
    name: str
    value: str

class AchievementItem(CamelCaseModel):
    description: str

class CertificationItem(CamelCaseModel):
    name: str
    issuer: str
    date: str

class ResumeData(CamelCaseModel):
    personal_info: PersonalInfo
    education: List[Education]
    work_experience: List[WorkExperience]
    projects: List[Project]
    skills: List[SkillItem]
    achievements: List[AchievementItem]
    certifications: List[CertificationItem]

class GenerationRequest(CamelCaseModel):
    template_name: str
    resume_data: ResumeData