import logging
import json
from io import BytesIO
from typing import Dict, Any, List, Optional

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse

from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, ListFlowable, ListItem, HRFlowable
)
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.schemas import (
    StartRequest, StartResponse, SessionRequest, RegenerateRequest,
    PDFRequest, CaseStudyResponse, LinkedInTextResponse,
    Project, ClientSPOC, TeamMember, ProjectFile
)

from app.agents.ghostwriter_agent import GhostwriterAgent
from app.core.session_store import session_store
from app.core.ttl_manager import TTLManager

# ==========================================================
# APP INIT
# ==========================================================

app = FastAPI(title="Ghostwriter API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ==========================================================
# DEPENDENCIES
# ==========================================================

def get_agent():
    return GhostwriterAgent()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==========================================================
# LIFECYCLE
# ==========================================================

ttl_manager = TTLManager(
    cleanup_callback=session_store.cleanup_expired,
    interval_seconds=3600
)

@app.on_event("startup")
def startup():
    ttl_manager.start()
    logger.info("TTL Manager started.")

@app.on_event("shutdown")
def shutdown():
    ttl_manager.stop()
    logger.info("TTL Manager stopped.")

# ==========================================================
# SESSION START FROM PROJECT CODE
# ==========================================================

@app.post("/ghostwriter/start/{project_code}", response_model=StartResponse)
def start_session_from_project(project_code: str, db: Session = Depends(get_db)):
    # 1. Fetch project
    project = db.query(Project).filter(Project.project_code == project_code).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # 2. Fetch SPOC
    spoc = db.query(ClientSPOC.spoc_name).filter(ClientSPOC.project_id == project.project_id).first()

    # 3. Fetch team members (formatted as dicts for the Agent)
    team_query = db.query(TeamMember.name).filter(TeamMember.project_id == project.project_id).all()
    team_list = [{"name": member[0]} for member in team_query]

    # 4. Fetch s3_urls
    files = db.query(ProjectFile.s3_url).filter(ProjectFile.project_id == project.project_id).all()

    # 5. Construct metadata (Unified keys)
    metadata = {
        "project_id": project.project_id,
        "project_name": project.project_name,
        "brand_company": project.brand_company,
        "status": project.status,
        "spoc_name": spoc[0] if spoc else "N/A",
        "team_members": team_list,  # Changed from 'team' to 'team_members'
        "s3_urls": [f[0] for f in files]
    }

    session_id = session_store.create_session(metadata=metadata)
    return StartResponse(session_id=session_id)

# ==========================================================
# CASE STUDY GENERATION
# ==========================================================

@app.post("/ghostwriter/case-study/text", response_model=CaseStudyResponse)
def generate_case_study(request: SessionRequest, agent: GhostwriterAgent = Depends(get_agent)):
    session = session_store.get_session(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Invalid session")

    metadata = session["metadata"]
    case_text = agent.generate_case_study(sow_data=metadata)

    session.setdefault("case_study_versions", []).append(case_text)
    version = len(session["case_study_versions"])

    return CaseStudyResponse(version=version, case_study_text=case_text)

@app.post("/ghostwriter/case-study/regenerate", response_model=CaseStudyResponse)
def regenerate_case_study(request: RegenerateRequest, agent: GhostwriterAgent = Depends(get_agent)):
    session = session_store.get_session(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Invalid session")

    case_text = agent.generate_case_study(
        sow_data=session["metadata"], 
        custom_prompt=request.custom_prompt
    )

    session.setdefault("case_study_versions", []).append(case_text)
    version = len(session["case_study_versions"])

    return CaseStudyResponse(version=version, case_study_text=case_text)

# ==========================================================
# LINKEDIN TEXT GENERATION
# ==========================================================

@app.post("/ghostwriter/linkedin/text", response_model=LinkedInTextResponse)
def generate_linkedin_text(request: SessionRequest, agent: GhostwriterAgent = Depends(get_agent)):
    session = session_store.get_session(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Invalid session")

    case_versions = session.get("case_study_versions", [])
    if not case_versions:
        raise HTTPException(status_code=400, detail="Generate case study first.")

    # FIX: Use .get("team_members") to match metadata construction
    team_data = session["metadata"].get("team_members", [])

    linkedin_text = agent.generate_linkedin_text(
        case_study_text=case_versions[-1],
        team_details=team_data
    )

    session.setdefault("linkedin_versions", []).append(linkedin_text)
    return LinkedInTextResponse(version=len(session["linkedin_versions"]), linkedin_text=linkedin_text)

@app.post("/ghostwriter/linkedin/regenerate", response_model=LinkedInTextResponse)
def regenerate_linkedin_text(request: RegenerateRequest, agent: GhostwriterAgent = Depends(get_agent)):
    session = session_store.get_session(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Invalid session")

    case_versions = session.get("case_study_versions", [])
    if not case_versions:
        raise HTTPException(status_code=400, detail="Generate case study first.")

    # FIX: Consistency with team_members key
    team_data = session["metadata"].get("team_members", [])

    linkedin_text = agent.generate_linkedin_text(
        case_study_text=case_versions[-1],
        team_details=team_data,
        # Ensure your Agent's regenerate_linkedin_text method exists or use logic here
    )

    session.setdefault("linkedin_versions", []).append(linkedin_text)
    return LinkedInTextResponse(version=len(session["linkedin_versions"]), linkedin_text=linkedin_text)

# ==========================================================
# IMAGE GENERATION
# ==========================================================

@app.post("/ghostwriter/linkedin/image")
def generate_linkedin_post_image(request: SessionRequest, agent: GhostwriterAgent = Depends(get_agent)):
    session = session_store.get_session(request.session_id)
    if not session or not session.get("case_study_versions"):
        raise HTTPException(status_code=400, detail="Valid session and case study required.")

    try:
        file_path = agent.generate_linkedin_post_image(case_study_text=session["case_study_versions"][-1])
        return FileResponse(file_path, media_type="image/jpeg", filename="linkedin_post.jpg")
    except Exception as e:
        logger.exception("Image generation failed")
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================================
# PDF GENERATION
# ==========================================================

@app.post("/ghostwriter/case-study/pdf")
def generate_case_study_pdf(request: PDFRequest):
    session = session_store.get_session(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Invalid session")

    try:
        content = session["case_study_versions"][request.version - 1]
    except (IndexError, KeyError):
        raise HTTPException(status_code=404, detail="Version not found")

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    
    # Simple story builder (Logic preserved from your snippet)
    story = [Paragraph("Case Study", styles["Heading1"]), Spacer(1, 0.2*inch)]
    for line in content.split("\n"):
        if line.strip():
            story.append(Paragraph(line, styles["BodyText"]))
            story.append(Spacer(1, 0.1*inch))
    
    doc.build(story)
    buffer.seek(0)

    return StreamingResponse(
        buffer, 
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=case_study_v{request.version}.pdf"}
    )