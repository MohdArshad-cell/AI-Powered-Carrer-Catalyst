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

# Originally from: scripts2/cl_prompt_step1_analysis.txt
PROMPT_1 = """
You are an expert data extractor and career analyst. Your task is to dissect the provided resume and job description to pull out specific, critical information for building a cover letter.
Resume Content:
{resume_content}

Job Description:
{job_description}

CRITICAL EXTRACTION TASK:

From the Resume:

candidate_name

candidate_address

candidate_phone

candidate_email

candidate_linkedin

candidate_github (if available)

candidate_portfolio (if available)

From the Job Description:

job_title

company_name

Analysis:

talking_points: Extract the top 3-4 most compelling connections between the candidate's experience and the job requirements.
company_tone: Determine the company's tone (e.g., "formal and corporate", "energetic and innovative", "mission-driven and collaborative").
Output Format:
Return ONLY a single, flat JSON object with the keys listed above.
If a piece of information (like a GitHub URL) is not found, return an empty string "" for its value.
Do not nest the JSON.
"""

# Originally from: scripts2/cl_prompt_step2_outline.txt
PROMPT_2 = """
You are a content strategist. Your task is to take the extracted data and structure it into a logical outline for a professional cover letter.
Extracted Data (JSON):
{analysis_json}

Task:
Create a JSON object that outlines the cover letter.
The structure should include:

A header object containing all the candidate's contact details, the date, and the company's details.
A subject_line string.

An introduction string.

A body_paragraphs array of strings, one for each talking point.

A conclusion string.
Output Format:
Return ONLY a structured JSON object representing the complete cover letter's structure and content plan.
The date should be the current date.
"""

# Originally from: scripts2/cl_prompt_step3_draft.txt
PROMPT_3 = """
You are an expert human copywriter with 20 years of experience writing professional correspondence.
Your writing is clear, confident, and feels completely natural. You NEVER use robotic or overly complex language.
Your task is to write a cover letter based on the provided outline.
Cover Letter Outline (JSON):
{outline_json}

Original Resume Content (for context):
{resume_content}

Original Job Description (for context):
{job_description}

CRITICAL DRAFTING RULES:

Use Exact Data: You MUST use the exact contact details, names, and date provided in the header of the outline.
DO NOT use placeholders like [Your Address].

Format Correctly:

The output must be plain text.

Create a standard business letter format.
The subject line MUST be formatted exactly as: Subject: Application for [Job Title] - [Candidate Name].
DO NOT use any markdown formatting like ** or ##. The text should be clean.
Write Like a Human:

Flesh out the body_paragraphs from the outline, weaving them into a smooth, compelling narrative.
The tone should be professional, confident, and align with the company_tone identified in the analysis. Avoid clichés and AI-sounding phrases.
Vary sentence structure to make the letter engaging to read.
Output Format:
Return ONLY the complete, fully-formatted, plain text of the cover letter.
"""

# Originally from: scripts2/cl_prompt_step4_review.txt
PROMPT_4 = """
You are a meticulous editor and senior hiring manager. Your final task is to review the generated cover letter draft and provide a final, polished version.
You are the last line of quality control.

Original Analysis & Extracted Data (JSON):
{analysis_json}

Cover Letter Draft:
{cover_letter_draft}

Instructions:
Review the LaTeX draft against the plan and requirements.
Ask yourself:

No Placeholders: Did the writer correctly use the candidate's real contact information?
Or did it mistakenly use placeholders like [Your Phone Number]? Correct this immediately if found.
Correct Formatting: Is the subject line formatted correctly? Is there any unwanted markdown (like **)? Remove it.
Human Tone & Impact: Does the letter sound like it was written by a confident professional, not an AI?
Is it persuasive? Make minor edits to improve flow, conciseness, and natural language.
Output Format:
Provide the final, perfected, and complete plain text of the cover letter. Your output should contain nothing else.
"""

# --- HELPER FUNCTIONS ---

@contextlib.contextmanager
def suppress_stderr():
    """A context manager to temporarily suppress SDK warnings."""
    original_stderr = sys.stderr
    sys.stderr = open(os.devnull, 'w', encoding='utf-8')
    try:
        yield
    finally:
        sys.stderr.close()
        sys.stderr = original_stderr

def call_gemini(prompt):
    """Calls the Gemini API and returns the text response."""
    with suppress_stderr():
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel(model_name=MODEL_NAME)
        response = model.generate_content(prompt)
    return response.text

def clean_json(json_string):
    """Extracts the first valid JSON object or array from a string."""
    match = re.search(r'\{[\s\S]*\}|\[[\s\S]*\]', json_string)
    if match:
        return match.group(0)
    else:
        raise ValueError(f"No valid JSON found in AI response: {json_string}")

def read_input_from_stdin():
    """Reads the combined input from stdin and splits it by the delimiter."""
    try:
        full_input = sys.stdin.read()
        parts = full_input.split('\n---DELIMITER---\n')
        if len(parts) != 2:
            # Fallback or error handling if delimiter is missing
            print("Error: Invalid input format. Expected delimiter.", file=sys.stderr)
            sys.exit(1)
        return parts[0], parts[1] # resume_content, job_description
    except Exception as e:
        print(f"Error reading stdin: {e}", file=sys.stderr)
        sys.exit(1)

# --- MAIN EXECUTION ---

def main():
    if not API_KEY:
        print("Error: GOOGLE_API_KEY environment variable not found.", file=sys.stderr)
        sys.exit(1)

    try:
        resume_content, job_description = read_input_from_stdin()

        # Step 1: Analysis
        prompt1 = PROMPT_1.format(job_description=job_description, resume_content=resume_content)
        analysis_str = call_gemini(prompt1)
        analysis_json = json.loads(clean_json(analysis_str))
        
        # Step 2: Outlining
        prompt2 = PROMPT_2.format(analysis_json=json.dumps(analysis_json, indent=2))
        outline_str = call_gemini(prompt2)
        outline_json = json.loads(clean_json(outline_str))

        # Step 3: Drafting
        prompt3 = PROMPT_3.format(outline_json=json.dumps(outline_json, indent=2), resume_content=resume_content, job_description=job_description)
        cover_letter_draft = call_gemini(prompt3)

        # Step 4: Reviewing
        prompt4 = PROMPT_4.format(cover_letter_draft=cover_letter_draft, analysis_json=json.dumps(analysis_json, indent=2))
        final_cover_letter = call_gemini(prompt4)
        
        # Send the final result to stdout for the Java application to capture
        print(final_cover_letter)

    except Exception as e:
        print(f"A critical error occurred during the AI generation process: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()