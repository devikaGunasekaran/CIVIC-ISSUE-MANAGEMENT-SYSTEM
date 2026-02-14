"""
FastAPI wrapper for AI Civic Issue Agents
"""

from fastapi import FastAPI, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional
import shutil
import os

from system import CivicAIAgentSystem, CitizenInput

app = FastAPI(title="AI Civic Issue Reporting API")

agent_system = CivicAIAgentSystem()


class IssueRequest(BaseModel):
    text: Optional[str] = None
    gps_coordinates: Optional[str] = None


@app.post("/report/text")
def report_text_issue(request: IssueRequest):
    citizen_input = CitizenInput(
        text=request.text,
        gps_coordinates=request.gps_coordinates
    )
    result = agent_system.process_issue(citizen_input)
    return result.__dict__


@app.post("/report/image")
async def report_with_image(
    text: str = Form(...),
    gps_coordinates: Optional[str] = Form(None),
    image: UploadFile = File(...)
):
    image_path = f"temp_{image.filename}"
    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    citizen_input = CitizenInput(
        text=text,
        image_path=image_path,
        gps_coordinates=gps_coordinates
    )

    result = agent_system.process_issue(citizen_input)

    os.remove(image_path)

    return result.__dict__


@app.get("/health")
def health_check():
    return {"status": "AI Agents Running"}
