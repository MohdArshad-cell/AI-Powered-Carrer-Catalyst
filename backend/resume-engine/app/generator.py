import os
import json
import subprocess
import uuid
import re
import tempfile
from jinja2 import Environment, FileSystemLoader

# A function to escape most special LaTeX characters
def escape_latex(text):
    if not isinstance(text, str):
        return text
    conv = {
        '&': r'\&', '%': r'\%', '$': r'\$', '#': r'\#', '_': r'\_',
        '{': r'\{', '}': r'\}', '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}', '\\': r'\textbackslash{}',
    }
    regex = re.compile('|'.join(re.escape(key) for key in sorted(conv.keys(), key = len, reverse=True)))
    return regex.sub(lambda match: conv[match.group()], text)

# NEW: A less aggressive filter that allows some commands like \textbf{}
def safe_latex(text):
    if not isinstance(text, str):
        return text
    conv = {
        '&': r'\&', '%': r'\%', '$': r'\$', '#': r'\#', '_': r'\_',
    }
    regex = re.compile('|'.join(re.escape(key) for key in sorted(conv.keys(), key = len, reverse=True)))
    return regex.sub(lambda match: conv[match.group()], text)


class ResumeGenerator:
    def __init__(self, template_dir="app/templates"):
        self.template_dir = template_dir
        self.env = Environment(
            loader=FileSystemLoader(self.template_dir),
            block_start_string='\\BLOCK{',
            block_end_string='}',
            variable_start_string='\\VAR{',
            variable_end_string='}',
            comment_start_string='\\#{',
            comment_end_string='}',
            trim_blocks=True,
            autoescape=False,
        )
        self.env.filters['escape_tex'] = escape_latex
        self.env.filters['safe_tex'] = safe_latex # <-- ADD THIS LINE to register the filter
        
        self.temp_dir = os.path.join(tempfile.gettempdir(), "resume_generator")
        os.makedirs(self.temp_dir, exist_ok=True)
        
        self.pdflatex_path = r"D:\MIKTex\miktex\bin\x64\pdflatex.exe"

    def generate(self, template_name: str, data: dict):
        session_id = str(uuid.uuid4())
        output_dir = os.path.join(self.temp_dir, session_id)
        os.makedirs(output_dir)

        main_tex_filename = f"{template_name}.tex"
        template = self.env.get_template(f"{template_name}/{main_tex_filename}")
        latex_source = template.render(resume_data=data)
        
        tex_filepath = os.path.join(output_dir, "resume.tex")
        with open(tex_filepath, 'w', encoding='utf-8') as f:
            f.write(latex_source)

        cmd = [self.pdflatex_path, "resume.tex"]
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True, cwd=output_dir)
            subprocess.run(cmd, check=True, capture_output=True, text=True, cwd=output_dir)
        except subprocess.CalledProcessError as e:
            print("LaTeX compilation failed. See log below:")
            print(e.stdout)
            raise RuntimeError(f"LaTeX Error: {e.stdout}")

        pdf_filepath = os.path.join(output_dir, "resume.pdf")
        
        if not os.path.exists(pdf_filepath):
            raise FileNotFoundError("PDF generation failed, file not found.")

        json_filepath = os.path.join(output_dir, "resume.json")
        with open(json_filepath, 'w') as f:
            json.dump(data, f, indent=4)
        
        return {
            "pdf_path": pdf_filepath,
            "tex_path": tex_filepath,
            "json_path": json_filepath
        }