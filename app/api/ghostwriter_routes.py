from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List

from app.services.generation_service import GenerationService
from app.services.regeneration_service import RegenerationService

router = APIRouter(
    prefix="/ghostwriter",
    tags=["Ghostwriter"]
)

# =====================================================
# REQUEST MODELS
# =====================================================

class CaseStudyRequest(BaseModel):
    sow_data: Dict[str, Any]
    custom_prompt: Optional[str] = None


class LinkedInTextRequest(BaseModel):
    case_study_text: str
    team_details: List[Dict[str, str]]
    custom_prompt: Optional[str] = None


class LinkedInImageRequest(BaseModel):
    case_study_text: str
    custom_prompt: Optional[str] = None


# =====================================================
# ROUTES
# =====================================================

@router.post("/case-study")
def generate_case_study(request: CaseStudyRequest):
    try:
        if request.custom_prompt:
            # 🔁 Use RegenerationService
            result = RegenerationService.regenerate_case_study(
                metadata=request.sow_data,
                custom_prompt=request.custom_prompt
            )
        else:
            # 🆕 Use GenerationService
            result = GenerationService.generate_case_study(
                metadata=request.sow_data
            )

        return {"case_study": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/linkedin/text")
def generate_linkedin_text(request: LinkedInTextRequest):
    try:
        if request.custom_prompt:
            # 🔁 Regenerate LinkedIn text
            result = RegenerationService.regenerate_linkedin_text(
                case_study_text=request.case_study_text,
                team_details=request.team_details,
                custom_prompt=request.custom_prompt
            )
        else:
            # 🆕 Generate LinkedIn text
            metadata = {
                "project_name": "Project",
                "domain": "Technology",
                "team": request.team_details
            }

            result = GenerationService.generate_linkedin_text(metadata)

        return {"linkedin_text": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/linkedin/image-prompt")
def generate_linkedin_image_prompt(request: LinkedInImageRequest):
    try:
        if request.custom_prompt:
            # 🔁 Regenerate image prompt
            result = RegenerationService.regenerate_linkedin_image_prompt(
                case_study_text=request.case_study_text,
                custom_prompt=request.custom_prompt
            )
        else:
            # 🆕 Generate image prompt
            result = GenerationService.generate_linkedin_image_bytes()

        return {"image_prompt": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))