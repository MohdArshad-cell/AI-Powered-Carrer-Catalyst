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

# Step 1: Analyze the JD to find key skills
PROMPT_STEP_1 = """
Analyze the following Job Description (JD).
Identify the top 3 Technical Skills and top 2 Behavioral Traits required.
Return the result as a valid JSON object.

JD:
{job_description}
"""

# Step 2: Generate 10 Questions + Answers based on the analysis
PROMPT_STEP_2 = """
Based on this job description analysis:
{analysis_json}

Act as an expert Technical Recruiter and Hiring Manager. Generate a comprehensive list of 10 interview questions tailored specifically to this role.

The questions must cover these categories:
1.  **Introduction & Experience** (1-2 questions): standard opening but tailored to the JD.
2.  **Hard Skills & Technical Proficiency** (4-5 questions): deep dive into specific tools/languages mentioned in the JD.
3.  **Behavioral & Situational** (3-4 questions): using the STAR method, focusing on challenges likely to happen in this specific job.

For EACH question, provide a "Model Answer" or "Key Talking Points" that a candidate should mention to impress the interviewer.

Return the output as a RAW JSON list of objects with this exact structure:
[
  {{
    "question": "The interview question here...",
    "answer": "The ideal answer or key points to cover..."
  }},
  ...
]

Do not include markdown formatting (like ```json). Just the raw JSON.
"""

# --- HELPER FUNCTIONS ---

@contextlib.contextmanager
def suppress_stderr():
    original_stderr = sys.stderr
    sys.stderr = open(os.devnull, 'w', encoding='utf-8')
    try:
        yield
    finally:
        sys.stderr.close()
        sys.stderr = original_stderr

def call_gemini(prompt):
    with suppress_stderr():
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel(MODEL_NAME)
        return model.generate_content(prompt).text

def clean_json(text):
    # Removes markdown code blocks if present
    match = re.search(r'```(json)?\s*(\{[\s\S]*\}|\[[\s\S]*\])\s*```', text)
    if match:
        return match.group(2)
    
    # Fallback to finding the first array or object
    match = re.search(r'\{[\s\S]*\}|\[[\s\S]*\]', text)
    return match.group(0) if match else "[]"

def main():
    # Read JD from Stdin (passed by Java)
    try:
        input_data = sys.stdin.read().strip()
        if not input_data: 
            # Fallback for empty input
            print("[]")
            sys.exit(0)
        job_description = input_data
    except Exception:
        sys.exit(1)

    if not API_KEY:
        print("Error: GOOGLE_API_KEY not found.", file=sys.stderr)
        sys.exit(1)

    # --- CHAIN PROMPTING START ---
    
    # STEP 1: Deep Analysis
    try:
        p1 = PROMPT_STEP_1.format(job_description=job_description)
        analysis_raw = call_gemini(p1)
        analysis_json = clean_json(analysis_raw)
    except Exception as e:
        print(f"Error in Step 1: {e}", file=sys.stderr)
        print("[]") # Return empty JSON to avoid crashing Java
        sys.exit(1)

    # STEP 2: Question Generation
    try:
        p2 = PROMPT_STEP_2.format(analysis_json=analysis_json)
        questions_raw = call_gemini(p2)
        questions_json = clean_json(questions_raw)
        
        # Output strictly JSON to Java (Standard Output)
        print(questions_json) 
    except Exception as e:
        print(f"Error in Step 2: {e}", file=sys.stderr)
        print("[]")
        sys.exit(1)

if __name__ == "__main__":
    main()