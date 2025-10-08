import sys
import os
import json
import re
import google.generativeai as genai
import contextlib

# --- CONFIGURATION ---
# Reads the API key from the environment variable passed by the Java AiService
API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_NAME = "gemini-2.5-flash-lite" # Using a more robust model is recommended

# --- HELPER FUNCTIONS (These are correct and do not need changes) ---

def load_file(file_path: str) -> str:
    """Reads and returns the content of a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: Prompt file not found at {file_path}", file=sys.stderr)
        sys.exit(1)

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
    match = re.search(r'```(json)?\s*(\{[\s\S]*\}|\[[\s\S]*\])\s*```', json_string)
    if match:
        return match.group(2)
    
    match = re.search(r'\{[\s\S]*\}|\[[\s\S]*\]', json_string)
    if match:
        return match.group(0)
    
    raise ValueError(f"No valid JSON object or array found in the AI's response: {json_string}")


# --- MAIN FUNCTION (CORRECTED) ---
def main():
    """Main execution function to run the 3-step evaluation."""
    if not API_KEY:
        print("Error: GEMINI_API_KEY environment variable not found or is not set.", file=sys.stderr)
        sys.exit(1)

    try:
        # *** FIX: Reads from standard input, exactly like tailor.py ***
        full_input = sys.stdin.read()
        parts = full_input.split("\n---DELIMITER---\n")
        
        if len(parts) != 2:
            print("Error: Input from Java did not contain the correct delimiter.", file=sys.stderr)
            sys.exit(1)
            
        resume_content = parts[0]
        job_description = parts[1]
        # ***************************************************************

        script_dir = os.path.dirname(__file__)

        # The rest of your proven 3-step evaluation logic remains unchanged
        # STEP 1: Analyze the Job Description
        prompt1_template = load_file(os.path.join(script_dir, 'prompt_step1_jd_analysis.txt'))
        prompt1 = prompt1_template.format(job_description=job_description)
        jd_analysis_str = call_gemini_api(prompt1)
        jd_analysis_json = json.loads(clean_json_string(jd_analysis_str))

        # STEP 2: Analyze the Resume
        prompt2_template = load_file(os.path.join(script_dir, 'prompt_step2_resume_analysis.txt'))
        prompt2 = prompt2_template.format(resume_content=resume_content)
        resume_analysis_str = call_gemini_api(prompt2)
        resume_analysis_json = json.loads(clean_json_string(resume_analysis_str))

        # STEP 3: Perform the Comprehensive ATS Evaluation
        prompt3_template = load_file(os.path.join(script_dir, 'prompt_step3_ats_evaluation.txt'))
        prompt3 = prompt3_template.format(
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