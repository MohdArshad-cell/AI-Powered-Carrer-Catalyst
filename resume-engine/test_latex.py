import subprocess
import os

# --- PASTE THE EXACT PATH to pdflatex.exe YOU FOUND EARLIER ---
pdflatex_path = r"D:\MIKTex\miktex\bin\x64\pdflatex.exe"
# --------------------------------------------------------------------

# A minimal LaTeX document that requires the 'geometry' package
latex_content = r"""
\documentclass{article}
\usepackage{geometry}
\begin{document}
Hello, World!
\end{document}
"""

# Write the content to a test file
try:
    with open("test.tex", "w") as f:
        f.write(latex_content)
    print("SUCCESS: Created test.tex file.")
except Exception as e:
    print(f"ERROR: Could not create test.tex file: {e}")


# Try to compile the test file
print("\n--- Attempting to compile with pdflatex ---")
cmd = [pdflatex_path, "test.tex"]

try:
    # We run subprocess directly to see the full output
    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
    print("\nSUCCESS: PDF compilation was successful!")
    print("Output from pdflatex:")
    print(result.stdout)
except subprocess.CalledProcessError as e:
    print("\nERROR: PDF compilation failed!")
    print("This is the REAL error message from MiKTeX:")
    print("-------------------------------------------")
    print(e.stdout) # This will show us the LaTeX log
    print("-------------------------------------------")
except FileNotFoundError:
    print(f"ERROR: The path to pdflatex.exe is WRONG. Could not find the file at: {pdflatex_path}")