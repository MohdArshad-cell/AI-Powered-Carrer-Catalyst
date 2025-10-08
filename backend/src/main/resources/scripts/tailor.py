import sys
import os
import json
import re
import google.generativeai as genai
import contextlib

# --- CONFIGURATION ---
# The API key is now read from the environment variable passed by the Java service
API_KEY = os.getenv("GOOGLE_API_KEY") 
MODEL_NAME = "gemini-2.5-flash-lite" # Updated to a valid and recommended model

# --- HELPER FUNCTIONS ---

def load_file(file_path: str) -> str:
    """Reads and returns the content of a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        # Use stderr for error messages so Java can capture them
        print(f"Error: Required file not found at {file_path}", file=sys.stderr)
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
    match = re.search(r'\{[\s\S]*\}|\[[\s\S]*\]', json_string)
    if match:
        return match.group(0)
    else:
        raise ValueError(f"No valid JSON object or array found in the AI's response: {json_string}")

def clean_final_latex(text: str) -> str:
    """Performs a final, safer cleaning of the LaTeX code."""
    start_index = text.find(r'\documentclass')
    if start_index == -1:
        # Fallback if documentclass is missing
        return text.strip() 
    clean_text = text[start_index:]
    replacements = { "’": "'", "–": "--", "—": "--", "\uFFFD": "--" }
    for old, new in replacements.items():
        clean_text = clean_text.replace(old, new)
    clean_text = re.sub(r'(\d)\%', r'\1\\%', clean_text)
    clean_text = re.sub(r'(?<=\w)&(?=\w)', r'\\&', clean_text)
    clean_text = clean_text.replace('{{', '{').replace('}}', '}')
    return clean_text.strip()

# --- NEW: Function to read from stdin ---
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
# ----------------------------------------

def main():
    """Main execution function to run the 4-step prompt chain."""
    
    # --- MODIFIED: Use the new stdin function instead of sys.argv ---
    resume_content, job_description = read_input_from_stdin()
    # -----------------------------------------------------------------

    if not API_KEY:
        print("Error: GOOGLE_API_KEY environment variable was not received from Java service.", file=sys.stderr)
        sys.exit(1)
    
    script_dir = os.path.dirname(__file__)

    try:
        # Step 1: Analyze Job Description
        prompt1_template = load_file(os.path.join(script_dir, 'prompt_step1_jd_analysis.txt'))
        prompt1 = prompt1_template.format(job_description=job_description)
        jd_analysis_str = call_gemini_api(prompt1)
        jd_analysis_json = json.loads(clean_json_string(jd_analysis_str))
    except Exception as e:
        print(f"A critical error occurred during STEP 1 (JD Analysis): {e}", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Step 2: Plan an ATS-friendly strategy
        prompt2_template = load_file(os.path.join(script_dir, 'prompt_step2_planning.txt'))
        prompt2 = prompt2_template.format(jd_analysis_json=json.dumps(jd_analysis_json, indent=2), resume_content=resume_content)
        strategic_plan_str = call_gemini_api(prompt2)
        strategic_plan_json = json.loads(clean_json_string(strategic_plan_str))
    except Exception as e:
        print(f"A critical error occurred during STEP 2 (Strategic Planning): {e}", file=sys.stderr)
        sys.exit(1)
    
    try:
        # Step 3: Draft the new resume sections
        # This assumes you might have a 'template.tex' file, if not, this part might need adjustment
        latex_template = "" # Default to empty if not used
        template_path = os.path.join(script_dir, 'template.tex')
        if os.path.exists(template_path):
            latex_template = load_file(template_path)
            
        prompt3_template = load_file(os.path.join(script_dir, 'prompt_step3_drafting.txt'))
        prompt3 = prompt3_template.format(strategic_plan_json=json.dumps(strategic_plan_json, indent=2), resume_content=resume_content, DEFAULT_LATEX_TEMPLATE=latex_template)
        latex_draft = call_gemini_api(prompt3)
    except Exception as e:
        print(f"A critical error occurred during STEP 3 (Draft Generation): {e}", file=sys.stderr)
        sys.exit(1)

    try:
        # Step 4: Critique and Refine
        prompt4_template = load_file(os.path.join(script_dir, 'prompt_step4_review.txt'))
        prompt4 = prompt4_template.format(jd_analysis_json=json.dumps(jd_analysis_json, indent=2), strategic_plan_json=json.dumps(strategic_plan_json, indent=2), latex_draft=latex_draft)
        final_latex_with_critique = call_gemini_api(prompt4)
        
        # NOTE: Your logic was to return LaTeX. If you want plain text, this might need changing.
        final_output = clean_final_latex(final_latex_with_critique)
        print(final_output) # This prints the final result to Java
    except Exception as e:
        print(f"A critical error occurred during STEP 4 (Critique and Refine): {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()