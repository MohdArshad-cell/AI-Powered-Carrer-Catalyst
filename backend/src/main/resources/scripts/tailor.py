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

PROMPT_STEP_1 = """
You are an expert technical recruiter and talent analyst. Your primary task is to dissect the provided job description and extract all critical information into a structured JSON format.
Pay close attention to both explicit requirements and implicit cultural cues.
**Job Description to Analyze:**
{job_description}

**Instructions:**
1. Extract all **required_skills** and **preferred_skills** into separate lists of strings. Include both technical and soft skills.
2. Extract the **key_responsibilities** into a list of strings.
3. Perform a **tone_analysis**.
Based on the language, word choice, and phrasing in the job description, determine the likely **company_culture** (e.g., "fast-paced startup," "formal corporate," "academic/research," "mission-driven non-profit") and the appropriate applicant **voice** (e.g., "energetic and innovative," "professional and reliable," "technical and data-driven").
**Output Format:**
Return ONLY the structured JSON object. Do not include any other text, comments, or explanations.
The JSON must have the keys: "required_skills", "preferred_skills", "key_responsibilities", and "tone_analysis".
"""

PROMPT_STEP_2 = """
You are a master resume strategist and career coach. Your task is to create a detailed, strategic plan to tailor the candidate's resume to the job requirements.
You will be given the candidate's plain text resume and a JSON object containing the job requirements and tone analysis from the previous step.
**Job Requirements & Tone Analysis (JSON):**
{jd_analysis_json}

**Candidate's Plain Text Resume:**
{resume_content}

**Instructions:**
1. **Gap & Match Analysis**: Briefly summarize how well the candidate's skills match the job requirements and identify the key gaps that need to be addressed.
2. **Strategic Section Reordering**: Based on the job's priorities, recommend if the main sections of the resume (e.g., Experience, Projects, Skills) should be reordered for maximum impact.
State the recommended order.
3. **Bullet Point Enhancement Plan**: For each bullet point in the candidate's Experience and Projects, provide a specific recommendation.
Suggest how to integrate keywords from the job requirements and rephrase the bullet to match the required tone.
4. **Plausible Metrics Suggestion**: For any bullet points that lack numbers, suggest a plausible and realistic metric that the user could add.
Frame it clearly as a suggestion (e.g., "Suggest adding a metric like 'improved processing time by ~15–20%'").
**Output Format:**
Output this plan as a structured JSON object. The main keys should be "gap_match_summary", "section_reordering_suggestion", and "bullet_point_enhancement_plan".
"""

PROMPT_STEP_3 = """
You are a meticulous and expert LaTeX resume writer. Your sole task is to act as a pure execution engine.
You will take a strategic plan and the original resume content and perfectly render it into the provided LaTeX template, applying all rules below without deviation.
---
### ## INPUTS

**Strategic Tailoring Plan (JSON):**
{strategic_plan_json}

**Original Plain Text Resume:**
{resume_content}

**LaTeX Template:**
{DEFAULT_LATEX_TEMPLATE}

---
### ## CORE DIRECTIVES

1.  Your primary guide is the **Strategic Tailoring Plan**.
You must implement every suggestion it contains for reordering, rephrasing, and enhancing content.
2.  Use the **Original Plain Text Resume** as the source of truth for all content that is not explicitly altered by the strategic plan.
3.  **DO NOT INVENT INFORMATION:** Do not add any skills or experiences that are not present in the original resume or suggested by the strategic plan.
---
### ## LATEX FORMATTING RULES

* **Custom Commands:** You must use the custom LaTeX commands (`\\resumeSubheading`, `\\resumeItem`, etc.) from the template to structure the content.
* **Argument Count:** The `\\resumeSubheading` command *always* takes four arguments (`{{arg1}}{{arg2}}{{arg3}}{{arg4}}`).
If an argument is empty, use an empty brace (`{{}}`).
* **Skills Section Structure:** For the 'Technical Skills' section, generate a separate `\\resumeItem` for each category (e.g., `\\resumeItem{{\\textbf{{Languages}}: Java, Python...}}`).
* **Special Characters:** You must escape all special LaTeX characters (e.g., `&` to `\\&`, `_` to `\\_`, `%` to `\\%`).
* **Bold Text:** Apply the `\\textbf{{}}` command to all Project Titles and for the labels in the Technical Skills section.
* **Valid Structure:** All bulleted text must be placed inside a `\\resumeItem` command.
Do not generate text in floating braces (`{{...}}`) or add extra `\\\\` commands where they don't belong.
* **One-Page Limit:** Strictly adhere to the one-page limit, using space optimization techniques as needed.
* **`\\resumeSubheading` Command:** This command MUST be used with four arguments in this exact order: `\\resumeSubheading{{Job Title}}{{Date}}{{Company}}{{Location}}`.
The `Date` (second argument) and `Location` (fourth argument) will be automatically right-aligned by the template.
Do not add `&` characters inside any of the four arguments.
---
### ## OUTPUT FORMAT

* Return ONLY the complete, compilable LaTeX code for the draft.
* Do not include comments or explanations.
* The response must begin with `\\documentclass` and end with `\\end{{document}}`.
"""

PROMPT_STEP_4 = """
You are a meticulous senior hiring manager at the target company.
Your final task is to review the generated LaTeX resume draft and provide a final, polished version.
You are the last line of quality control.

**Original Job Requirements & Tone Analysis (JSON):**
{jd_analysis_json}

**Strategic Tailoring Plan (JSON):**
{strategic_plan_json}

**Generated LaTeX Draft:**
{latex_draft}

**Instructions:**
Review the LaTeX draft against the plan and requirements.
Ask yourself:
1. **Adherence to Plan:** Does the draft perfectly implement every instruction from the strategic plan?
2. **Tone & Culture Fit:** Does the language and phrasing match the company's tone identified in the analysis?
3. **Impact & ATS Score:** Is the resume highly impactful and optimized for ATS scanners?
Are the most important qualifications immediately obvious?
4. **Final Polish:** Make any final, minor edits necessary to improve flow, conciseness, and impact.
5. **VALID LATEX STRUCTURE:** The final output must be a well-structured and complete LaTeX document.
Ensure all commands have the correct number of arguments and all environments (`\\begin...` / `\\end...`) are properly nested.
**Output Format:**
First, provide a brief, silent critique of the draft for your own reference inside **``** XML comment tags.
Then, on a new line, provide the **final, perfected, and complete** LaTeX code. Your output should contain nothing else.
"""

LATEX_TEMPLATE = r"""
%-------------------------
% Resume in Latex
% Author : Ibrahim Saleem
% LinkedIn: https://linkedin.com/ibrahimsaleem91
%------------------------

\documentclass[letterpaper,9.8pt]{article}
\usepackage{latexsym}
\usepackage[empty]{fullpage}
\usepackage{titlesec}
\usepackage[usenames,dvipsnames]{color}
\usepackage{enumitem}
\usepackage[hidelinks]{hyperref}
\usepackage{fancyhdr}
\usepackage{tabularx, multicol}

\pagestyle{fancy}
\fancyhf{}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}

% Adjust margins
\addtolength{\oddsidemargin}{-0.5in}
\addtolength{\evensidemargin}{-0.5in}
\addtolength{\textwidth}{1in}
\addtolength{\topmargin}{-0.7in}
\addtolength{\textheight}{1.35in}

\urlstyle{same}
\raggedbottom
\raggedright
\setlength{\tabcolsep}{0in}

\titleformat{\section}{
  \vspace{-10pt}\scshape\raggedright\large
}{}{0em}{}[\color{black}\titlerule \vspace{-7pt}]

% --- CORRECTED CUSTOM COMMANDS ---
\newcommand{\resumeItem}[1]{
  \item\small{
    {#1 \vspace{-3pt}}
  }
}

\newcommand{\resumeSubheading}[4]{
  \vspace{-1pt}\item
    \begin{tabular*}{0.97\textwidth}[t]{l@{\extracolsep{\fill}}r}
      \textbf{#1} & #2 \\
      \textit{\small#3} & \textit{\small #4} \\
    \end{tabular*}\vspace{-6pt}
}

\newcommand{\resumeProjectHeading}[2]{
    \item
    \begin{tabular*}{0.97\textwidth}{l@{\extracolsep{\fill}}r}
      \small#1 & #2 \\
    \end{tabular*}\vspace{-6pt}
}

\newcommand{\resumeItemListStart}{\begin{itemize}[leftmargin=*, label=$\bullet$]}
\newcommand{\resumeItemListEnd}{\end{itemize}\vspace{-5pt}}
\newcommand{\resumeSubHeadingListStart}{\begin{itemize}[leftmargin=0.15in, label={}]}
\newcommand{\resumeSubHeadingListEnd}{\end{itemize}}

%-------------------------------------------
%%%%%%  RESUME STARTS HERE  %%%%%%%%%%%%%%%%%%%%%%%%%%%%


\begin{document}

%----------HEADING----------
\begin{center}
    \textbf{\Huge \scshape Jake Ryan} \\ \vspace{1pt}
    \small 123-456-7890 $|$ \href{mailto:x@x.com}{\underline{jake@su.edu}} $|$ 
    \href{https://linkedin.com/in/...}{\underline{linkedin.com/in/jake}} $|$
    \href{https://github.com/...}{\underline{github.com/jake}}
\end{center}


%-----------EDUCATION-----------
\section{Education}
  \resumeSubHeadingListStart
    \resumeSubheading
      {Southwestern University}{Georgetown, TX}
      {Bachelor of Arts in Computer Science, Minor in Business}{Aug. 2018 -- May 2021}
    \resumeSubheading
      {Blinn College}{Bryan, TX}
      {Associate's in Liberal Arts}{Aug. 2014 -- May 2018}
  \resumeSubHeadingListEnd


%-----------EXPERIENCE-----------
\section{Experience}
  \resumeSubHeadingListStart

    \resumeSubheading
      {Undergraduate Research Assistant}{June 2020 -- Present}
      {Texas A\&M University}{College Station, TX}
      \resumeItemListStart
        \resumeItem{Developed a REST API using FastAPI and PostgreSQL to store data from learning management systems}
        \resumeItem{Developed a full-stack web application using Flask, React, PostgreSQL and Docker to analyze GitHub data}
        \resumeItem{Explored ways to visualize GitHub collaboration in a classroom setting}
      \resumeItemListEnd
      
    \resumeSubheading
      {Information Technology Support Specialist}{Sep. 2018 -- Present}
      {Southwestern University}{Georgetown, TX}
      \resumeItemListStart
        \resumeItem{Communicate with managers to set up campus computers used on campus}
        \resumeItem{Assess and troubleshoot computer problems brought by students, faculty and staff}
        \resumeItem{Maintain upkeep of computers, classroom equipment, and 200 printers across campus}
      \resumeItemListEnd

    \resumeSubheading
      {Artificial Intelligence Research Assistant}{May 2019 -- July 2019}
      {Southwestern University}{Georgetown, TX}
      \resumeItemListStart
        \resumeItem{Explored methods to generate video game dungeons based off of \emph{The Legend of Zelda}}
        \resumeItem{Developed a game in Java to test the generated dungeons}
        \resumeItem{Contributed 50K+ lines of code to an established codebase via Git}
        \resumeItem{Conducted a human subject study to determine which video game dungeon generation technique is enjoyable}
        \resumeItem{Wrote an 8-page paper and gave multiple presentations on-campus}
        \resumeItem{Presented virtually to the World Conference on Computational Intelligence}
      \resumeItemListEnd

  \resumeSubHeadingListEnd


%-----------PROJECTS-----------
\section{Projects}
    \resumeSubHeadingListStart
      \resumeProjectHeading
          {\textbf{Gitlytics} $|$ \emph{Python, Flask, React, PostgreSQL, Docker}}{June 2020 -- Present}
          \resumeItemListStart
            \resumeItem{Developed a full-stack web application using with Flask serving a REST API with React as the frontend}
            \resumeItem{Implemented GitHub OAuth to get data from user's repositories}
            \resumeItem{Visualized GitHub data to show collaboration}
            \resumeItem{Used Celery and Redis for asynchronous tasks}
          \resumeItemListEnd
      \resumeProjectHeading
          {\textbf{Simple Paintball} $|$ \emph{Spigot API, Java, Maven, TravisCI, Git}}{May 2018 -- May 2020}
          \resumeItemListStart
            \resumeItem{Developed a Minecraft server plugin to entertain kids during free time for a previous job}
            \resumeItem{Published plugin to websites gaining 2K+ downloads and an average 4.5/5-star review}
            \resumeItem{Implemented continuous delivery using TravisCI to build the plugin upon new a release}
            \resumeItem{Collaborated with Minecraft server administrators to suggest features and get feedback about the plugin}
          \resumeItemListEnd
    \resumeSubHeadingListEnd

%-----------TECHNICAL SKILLS & CERTIFICATIONS-----------
\section{Technical Skills \& Certifications}
 \begin{itemize}[leftmargin=0.15in, label={}]
    \item {\small
     \textbf{Languages}{: Java, Python, C/C++, SQL (Postgres), JavaScript, HTML/CSS, R} \\
     \textbf{Frameworks}{: React, Node.js, Flask, JUnit, WordPress, Material-UI, FastAPI} \\
     \textbf{Developer Tools}{: Git, Docker, TravisCI, Google Cloud Platform, VS Code, Visual Studio, PyCharm, IntelliJ, Eclipse} \\
     \textbf{Libraries}{: pandas, NumPy, Matplotlib} \\
     \textbf{Certifications}{: Cisco Cybersecurity, ISC2 Certified in Cybersecurity (CC), CompTIA Security+ }
    }
 \end{itemize}

%-------------------------------------------
\end{document}
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

def call_gemini_api(prompt):
    with suppress_stderr():
        genai.configure(api_key=API_KEY)
        model = genai.GenerativeModel(model_name=MODEL_NAME)
        response = model.generate_content(prompt)
    return response.text

def clean_json_string(json_string):
    match = re.search(r'\{[\s\S]*\}|\[[\s\S]*\]', json_string)
    if match:
        return match.group(0)
    raise ValueError(f"No valid JSON found in response: {json_string}")

def clean_final_latex(text):
    start_index = text.find(r'\documentclass')
    if start_index == -1: return text.strip()
    return text[start_index:].strip()

def read_input_from_stdin():
    try:
        full_input = sys.stdin.read()
        parts = full_input.split("\n---DELIMITER---\n")
        if len(parts) != 2:
            # Fallback for manual testing without delimiter
            return full_input, ""
        return parts[0], parts[1]
    except Exception:
        return "", ""

def main():
    resume_content, job_description = read_input_from_stdin()

    if not API_KEY:
        print("Error: GOOGLE_API_KEY not found.", file=sys.stderr)
        sys.exit(1)

    try:
        # Step 1
        p1 = PROMPT_STEP_1.format(job_description=job_description)
        analysis_str = call_gemini_api(p1)
        analysis_json = json.loads(clean_json_string(analysis_str))

        # Step 2
        p2 = PROMPT_STEP_2.format(jd_analysis_json=json.dumps(analysis_json), resume_content=resume_content)
        plan_str = call_gemini_api(p2)
        plan_json = json.loads(clean_json_string(plan_str))

        # Step 3
        p3 = PROMPT_STEP_3.format(
            strategic_plan_json=json.dumps(plan_json), 
            resume_content=resume_content, 
            DEFAULT_LATEX_TEMPLATE=LATEX_TEMPLATE
        )
        latex_draft = call_gemini_api(p3)

        # Step 4
        p4 = PROMPT_STEP_4.format(
            jd_analysis_json=json.dumps(analysis_json), 
            strategic_plan_json=json.dumps(plan_json), 
            latex_draft=latex_draft
        )
        final_latex = call_gemini_api(p4)
        
        print(clean_final_latex(final_latex))

    except Exception as e:
        print(f"Error in tailor.py: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()