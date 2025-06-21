from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os

from main import flow_app  

app = FastAPI()


@app.post("/upload-srs/")
async def upload_srs(file: UploadFile = File(...)):
    if not file.filename.endswith(".docx"):
        raise HTTPException(status_code=400, detail="Only .docx files are supported.")

    contents = await file.read()
    if not contents.strip():
        raise HTTPException(status_code=400, detail="The uploaded .docx file is empty.")

    os.makedirs("temp", exist_ok=True)
    temp_path = f"temp/{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(contents)

    try:
        output = flow_app.invoke({"srs_file": temp_path})

        return JSONResponse(content={"message": "SRS processed successfully", "result": output})

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing SRS: {str(e)}")

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


