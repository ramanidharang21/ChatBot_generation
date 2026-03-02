from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Date, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.core.database import Base

# ==========================================================
# START SESSION
# ==========================================================

class StartRequest(BaseModel):
    project_id: str = Field(..., example="PRJ-001")
    project_name: str = Field(..., example="Digital Transformation Initiative")
    brand: str = Field(..., example="Acme Corp")
    domain: str = Field(..., example="FinTech")
    spoc: Dict[str, Any] = Field(..., example={"name": "John Doe", "email": "john@acme.com"})
    team: List[Dict[str, Any]] = Field(
        ...,
        example=[{"name": "Alice"}, {"name": "Bob"}]
    )
    sow_file_url: str = Field(..., example="https://example.com/sow.pdf")
    start_date: str = Field(..., example="2025-01-01")
    end_date: str = Field(..., example="2025-06-30")


class StartResponse(BaseModel):
    session_id: str


# ==========================================================
# SESSION REQUEST
# ==========================================================

class SessionRequest(BaseModel):
    session_id: str


# ==========================================================
# REGENERATE REQUEST
# ==========================================================

class RegenerateRequest(BaseModel):
    session_id: str
    custom_prompt: str


# ==========================================================
# PDF REQUEST
# ==========================================================

class PDFRequest(BaseModel):
    session_id: str
    version: int


# ==========================================================
# CASE STUDY RESPONSE
# ==========================================================

class CaseStudyResponse(BaseModel):
    version: int
    case_study_text: str


# ==========================================================
# LINKEDIN TEXT RESPONSE
# ==========================================================

class LinkedInTextResponse(BaseModel):
    version: int
    linkedin_text: str

class LinkedInImageResponse(BaseModel):
    version: int
    custom_prompt: Optional[str] = None


class Project(Base):
    __tablename__ = "projects"

    project_id = Column(Integer, primary_key=True, index=True)
    project_code = Column(String(20), unique=True, nullable=False)
    project_name = Column(String(255), nullable=False)
    brand_company = Column(String(255))
    domain = Column(String(100))
    status = Column(String(50))


class ClientSPOC(Base):
    __tablename__ = "client_spoc"

    spoc_id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.project_id"))
    spoc_name = Column(String(255))
    spoc_email = Column(String(255))


class TeamMember(Base):
    __tablename__ = "team_members"

    team_id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.project_id"))
    name = Column(String(255))
    role = Column(String(100))
    email = Column(String(255))


class ProjectFile(Base):
    __tablename__ = "project_files"

    file_id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.project_id"))
    s3_url = Column(Text)