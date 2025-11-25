import sys
import os
import json
import re
import google.generativeai as genai
import contextlib

# --- CONFIGURATION ---
API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_NAME = "gemini-2.5-flash-lite"

# --- EMBEDDED PROMPTS ---

# Originally from: scripts1/prompt_step1_jd_analysis.txt
PROMPT_JD = """
You are an expert technical recruiter and talent analyst. Your primary task is to dissect the provided job description and extract all critical information into a structured JSON format.
Pay close attention to both explicit requirements and implicit cultural cues.
**Job Description to Analyze:**
{job_description}

**Instructions:**
1. Extract all **required_skills** and **preferred_skills** into separate lists of strings. Include both technical and soft skills.
2. Extract the **key_responsibilities** into a list of strings.
3. Perform a **tone_analysis**.
Based on the language, determine the likely **company_culture** and the appropriate applicant **voice**.

**Output Format:**
Return ONLY the structured JSON object.
The JSON must have the keys: "required_skills", "preferred_skills", "key_responsibilities", and "tone_analysis".
"""

# Originally from: scripts1/prompt_step2_resume_analysis.txt
PROMPT_RESUME = """
You are an expert resume parser. Your task is to extract all key information from the candidate's resume into a structured JSON format.
**Candidate's Plain Text Resume:**
{resume_content}

**Instructions:**
1. Extract all **technical_skills** and **soft_skills** into separate lists of strings.
2. Provide a concise **experience_summary** as a single string, highlighting key accomplishments.
3. List all **project_titles** in a list of strings.

**Output Format:**
Return ONLY the structured JSON object.
The JSON must have the keys: "technical_skills", "soft_skills", "experience_summary", and "project_titles".
"""

# Originally from: scripts1/prompt_step3_ats_evaluation.txt
PROMPT_EVAL = """
You are an expert ATS (Applicant Tracking System) resume evaluator with 15+ years of technical recruiting experience.
Conduct a comprehensive analysis of how well the provided resume aligns with the specified job description using the structured data provided.
**STRUCTURED JOB DESCRIPTION:**
{job_description_json}

**STRUCTURED RESUME ANALYSIS:**
{resume_json}

**ORIGINAL RESUME FOR CONTEXT:**
{original_resume}

EVALUATION INSTRUCTIONS:

1.  First, using the STRUCTURED JOB DESCRIPTION, identify the top 10-15 critical requirements.
2.  For each requirement, analyze the STRUCTURED RESUME ANALYSIS and ORIGINAL RESUME to see if the candidate is qualified, looking for exact keyword matches, semantic relationships, and quantified experience.
3.  Evaluate resume optimization factors like the prominence of key qualifications and the use of job-specific language.
4.  Calculate a precise match score from 1-10 based on the percentage of key requirements effectively addressed (80%+ = 8-10, 60-79% = 6-7, etc.).
RESPONSE FORMAT:
Produce a Markdown report with the following sections.

SCORE: [whole number 1-10]

FEEDBACK: [150-300 word analysis including:
- Overall assessment of match quality
- 3-5 specific strengths (with examples from the resume)
- 3-5 specific improvement opportunities with actionable recommendations
- Key missing elements or terms that should be added]

IMPROVEMENT SUGGESTIONS: [Provide 2-3 specific, actionable suggestions for rephrasing bullet points from the original resume.
Show the "Original" bullet point and then a "Suggested" version that better incorporates keywords from the job description and quantifies achievements.
For example:
* Original: "Developed a full-stack web application using Flask, React, PostgreSQL and Docker."
* Suggested: "Engineered a full-stack web application leveraging a Python Flask REST API and React frontend, achieving a 20% reduction in page load times by optimizing PostgreSQL queries."]
DO NOT use any markdown formatting like ** or ##.
The text should be clean.
"""

# --- HELPER FUNCTIONS ---

@contextlib.contextmanager
def suppress_stderr():
    """A context manager to temporarily suppress stderr to hide library warnings."""
    original_stderr = sys.stderr
    sys.stderr = open(os.devnull, 'w', encoding='utf-8')
    try:
        yield
    finally:
        sys.stderr.close()
        sys.stderr = original_stderr

def call_gemini_api(prompt: str) -> str:
    """Calls the Gemini API with a given prompt and returns the text response."""
    with suppress_stderr():
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel(model_name=MODEL_NAME)
        response = model.generate_content(prompt)
    return response.text

def clean_json_string(json_string: str) -> str:
    """Finds and extracts the first valid JSON object or array from a string."""
    # Try to find JSON block first (```json ... ```)
    match = re.search(r'```(json)?\s*(\{[\s\S]*\}|\[[\s\S]*\])\s*```', json_string)
    if match:
        return match.group(2)
    
    # Fallback: Try to find raw JSON object
    match = re.search(r'\{[\s\S]*\}|\[[\s\S]*\]', json_string)
    if match:
        return match.group(0)
    
    raise ValueError(f"No valid JSON object or array found in the AI's response: {json_string}")

def read_input_from_stdin():
    """Reads resume and job description from stdin, separated by a delimiter."""
    try:
        full_input = sys.stdin.read()
        parts = full_input.split("\n---DELIMITER---\n")
        if len(parts) != 2:
            print("Error: Invalid input format from Java. Could not find delimiter.", file=sys.stderr)
            sys.exit(1)
        return parts[0], parts[1]
    except Exception as e:
        print(f"Error reading from stdin: {e}", file=sys.stderr)
        sys.exit(1)

# --- MAIN FUNCTION ---

def main():
    if not API_KEY:
        print("Error: GOOGLE_API_KEY environment variable was not received from Java service.", file=sys.stderr)
        sys.exit(1)

    try:
        resume_content, job_description = read_input_from_stdin()

        # STEP 1: Analyze the Job Description
        prompt1 = PROMPT_JD.format(job_description=job_description)
        jd_analysis_str = call_gemini_api(prompt1)
        jd_analysis_json = json.loads(clean_json_string(jd_analysis_str))

        # STEP 2: Analyze the Resume
        prompt2 = PROMPT_RESUME.format(resume_content=resume_content)
        resume_analysis_str = call_gemini_api(prompt2)
        resume_analysis_json = json.loads(clean_json_string(resume_analysis_str))

        # STEP 3: Perform the Comprehensive ATS Evaluation
        prompt3 = PROMPT_EVAL.format(
            job_description_json=json.dumps(jd_analysis_json, indent=2),
            resume_json=json.dumps(resume_analysis_json, indent=2),
            original_resume=resume_content
        )
        final_evaluation = call_gemini_api(prompt3)
        
        # The final report is printed to standard output, which Java will capture
        print(final_evaluation)

    except Exception as e:
        print(f"A critical error occurred during the evaluation process: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()