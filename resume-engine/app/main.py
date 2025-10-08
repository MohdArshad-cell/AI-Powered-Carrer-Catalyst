import zipfile
import io
import traceback
import os
from fastapi import FastAPI, HTTPException
from starlette.responses import StreamingResponse
from .models import GenerationRequest
from .generator import ResumeGenerator

app = FastAPI()
generator = ResumeGenerator()

# Health check endpoint
@app.get("/")
def read_root():
    return {"status": "ok", "message": "Resume Engine is running!"}

@app.post("/generate")
async def generate_resume(request: GenerationRequest):
    print("--- ✅ REQUEST RECEIVED ---")
    try:
        print(f"--- ⚙️ Using template: {request.template_name} ---")
        print(f"--- 📝 Received name: {request.resume_data.personal_info.full_name} ---")

        # This is the most likely point of failure.
        generated_files = generator.generate(
            request.template_name,
            request.resume_data.dict()
        )

        print(f"--- ✅ SUCCESS: Files generated at {generated_files} ---")

        pdf_path = generated_files.get("pdf_path")
        tex_path = generated_files.get("tex_path")
        json_path = generated_files.get("json_path")

        # Check if the files actually exist before trying to zip them
        for path in [pdf_path, tex_path, json_path]:
            if not path or not os.path.exists(path):
                print(f"--- ❌ ERROR: File path not found or does not exist: {path} ---")
                raise HTTPException(status_code=500, detail=f"Generated file not found: {path}")

        print("--- ⚙️ Zipping files... ---")
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED, False) as zip_file:
            zip_file.write(pdf_path, arcname="resume.pdf")
            zip_file.write(tex_path, arcname="resume.tex")
            zip_file.write(json_path, arcname="resume.json")

        zip_buffer.seek(0)
        print("--- ✅ SUCCESS: Zipping complete. Sending response. ---")

        return StreamingResponse(
            zip_buffer,
            media_type="application/x-zip-compressed",
            headers={"Content-Disposition": "attachment; filename=resume_files.zip"}
        )

    except Exception as e:
        print("--- ❌ CRITICAL ERROR CAUGHT ---")
        traceback.print_exc()  # This will print the full, detailed error to your logs
        print("---------------------------")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")