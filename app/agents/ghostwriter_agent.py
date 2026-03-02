import json
import logging
import boto3
import base64
import uuid
import os
from typing import Dict, Any, Optional, List
from pathlib import Path
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from strands import Agent
from strands.models import BedrockModel
from app.core.config import settings

logger = logging.getLogger(__name__)

class GhostwriterAgent:
    def __init__(self) -> None:
        """Initialize the LLM and the Strands Agent."""
        self.model = BedrockModel(
            model_id=settings.BEDROCK_MODEL_ID,
            temperature=settings.LLM_TEMPERATURE,
            max_tokens=settings.LLM_MAX_TOKENS,
        )

        self.agent = Agent(
            model=self.model,
            system_prompt=(
                "You are a senior B2B enterprise content strategist. "
                "You specialize in transforming technical documents into marketing assets. "
                "Maintain a professional tone, avoid fluff, and focus on ROI/KPIs."
            ),
        )
        logger.info("GhostwriterAgent initialized successfully.")

    def _get_bedrock_client(self):
        """Creates a Boto3 client using explicit session credentials for handshake stability."""
        session = boto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            aws_session_token=settings.AWS_SESSION_TOKEN,
            region_name=settings.AWS_REGION
        )
        return session.client("bedrock-runtime")

    def _execute_agent(self, prompt: str):
        """Cross-version compatibility for Strands SDK execution methods."""
        if hasattr(self.agent, "invoke"): return self.agent.invoke(prompt)
        if hasattr(self.agent, "run"): return self.agent.run(prompt)
        if callable(self.agent): return self.agent(prompt)
        raise RuntimeError("Unsupported Strands Agent execution method.")

    def _run(self, prompt: str) -> str:
        """Centralized execution wrapper with SDK response normalization."""
        try:
            response = self._execute_agent(prompt)
            if isinstance(response, str): return response.strip()
            if hasattr(response, "output"): return str(response.output).strip()
            if hasattr(response, "content"): return str(response.content).strip()
            return str(response).strip()
        except Exception as e:
            logger.exception("GhostwriterAgent execution failed.")
            raise RuntimeError(f"Agent execution failed: {str(e)}")

    def generate_case_study(self, sow_data: Dict[str, Any], custom_prompt: Optional[str] = None) -> str:
        """Transforms project metadata into a structured Case Study."""
        project_data = json.dumps(sow_data, indent=2)
        template = f"Generate a professional enterprise case study document based on this data:\n\n{project_data}"
        if custom_prompt: template += f"\n\nAdditional Instruction: {custom_prompt}"
        return self._run(template)

    def generate_linkedin_text(self, case_study_text: str, team_details: Optional[List[Dict[str, str]]] = None) -> str:
        """Generates LinkedIn copy. Handles missing team details gracefully."""
        # Defensive check for the 'KeyError: team' issue
        if not team_details or not isinstance(team_details, list):
            team_names = "our dedicated project team"
        else:
            names = [m.get("name", "").strip() for m in team_details if m.get("name")]
            team_names = ", ".join(names) if names else "our dedicated project team"

        template = (
            f"Create a high-impact LinkedIn post (150-250 words) from this case study. "
            f"Include an opening hook and tag #Shellkode. "
            f"Acknowledge the work of: {team_names}.\n\n"
            f"Source Case Study:\n{case_study_text}"
        )
        return self._run(template)

    def generate_linkedin_post_image(self, case_study_text: str) -> str:
        """Generates a premium 1024x1024 composite image for LinkedIn."""
        
        # 1. Extraction
        extraction_prompt = (
            "From the case study, extract a Headline (max 7 words) and a Supporting Metric (max 10 words). "
            "Return ONLY in this format:\nHeadline: [Text]\nMetric: [Text]"
        )
        extracted = self._run(f"{extraction_prompt}\n\nCase Study: {case_study_text}")
        
        headline, metric = "Enterprise Innovation", "Significant Efficiency Gains"
        for line in extracted.split("\n"):
            if "headline:" in line.lower(): headline = line.split(":", 1)[1].strip().replace('"', '')
            if "metric:" in line.lower(): metric = line.split(":", 1)[1].strip().replace('"', '')

        # 2. Background Generation
        try:
            bedrock = self._get_bedrock_client()
            bg_prompt = "Abstract futuristic corporate technology background, deep navy and cyan hues, sleek, professional, square composition, no text."
            body = json.dumps({
                "taskType": "TEXT_IMAGE",
                "textToImageParams": {"text": bg_prompt},
                "imageGenerationConfig": {"numberOfImages": 1, "width": 1024, "height": 1024, "cfgScale": 8.0}
            })
            response = bedrock.invoke_model(modelId="amazon.titan-image-generator-v2:0", body=body, contentType="application/json")
            img_b64 = json.loads(response["body"].read())["images"][0]
            image = Image.open(BytesIO(base64.b64decode(img_b64))).convert("RGB")
        except Exception as e:
            logger.error(f"Titan Background failed, using fallback: {e}")
            image = Image.new("RGB", (1024, 1024), (10, 30, 60))

        # 3. Visual Styling
        image = ImageEnhance.Brightness(image).enhance(0.4)
        draw = ImageDraw.Draw(image)
        
        # 4. Logo Overlay
        try:
            logo_path = Path(__file__).resolve().parent.parent.parent / "assets" / "logo.png"
            logo = Image.open(logo_path).convert("RGBA")
            logo.thumbnail((350, 120))
            image.paste(logo, ((image.width - logo.width) // 2, 80), logo)
        except:
            logger.warning("Logo asset missing.")

        # 5. Dynamic Typography
        try:
            f_head = ImageFont.truetype("arial.ttf", 75)
            f_met = ImageFont.truetype("arial.ttf", 50)
        except:
            f_head = f_met = ImageFont.load_default()

        def draw_wrapped_text(text, font, y_pos, color):
            words = text.split()
            lines = []
            current_line = []
            for word in words:
                current_line.append(word)
                bbox = draw.textbbox((0, 0), " ".join(current_line), font=font)
                if bbox[2] - bbox[0] > 800:
                    current_line.pop()
                    lines.append(" ".join(current_line))
                    current_line = [word]
            lines.append(" ".join(current_line))
            
            curr_y = y_pos
            for line in lines:
                draw.text((512, curr_y), line, font=font, fill=color, anchor="mm")
                curr_y += 85
            return curr_y

        # Render Text
        next_y = draw_wrapped_text(headline, f_head, 450, "white")
        draw_wrapped_text(metric, f_met, next_y + 40, "#00E5FF")

        # 6. Final Export
        os.makedirs("generated_images", exist_ok=True)
        file_path = f"generated_images/linkedin_post_{uuid.uuid4().hex}.jpg"
        image.save(file_path, "JPEG", quality=95)
        return file_path