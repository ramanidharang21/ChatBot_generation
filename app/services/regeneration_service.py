from typing import Dict, Any, List


class RegenerationService:
    """
    Handles regeneration logic for:
    - Case Study
    - LinkedIn Text
    - LinkedIn Image Prompt
    """

    # ==========================================================
    # CASE STUDY REGENERATION
    # ==========================================================

    @staticmethod
    def regenerate_case_study(
        metadata: Dict[str, Any],
        custom_prompt: str
    ) -> str:
        team_names = RegenerationService._format_team(
            metadata.get("team", [])
        )

        content = f"""
{custom_prompt}

Refined Case Study for "{metadata.get('project_name', 'Project')}":

Company:
{metadata.get('brand', 'Client')} operating in the {metadata.get('domain', 'Technology')} domain.

Project Duration:
{metadata.get('start_date', '')} to {metadata.get('end_date', '')}

Execution Summary:
Led by {team_names}, the initiative delivered scalable, sustainable, and measurable improvements.

Business Impact:
Improved operational efficiency, strengthened digital capabilities,
and enhanced customer experience.
"""

        return content.strip()

    # ==========================================================
    # LINKEDIN TEXT REGENERATION
    # ==========================================================

    @staticmethod
    def regenerate_linkedin_text(
        case_study_text: str,
        team_details: List[Dict[str, str]],
        custom_prompt: str
    ) -> str:
        team_names = RegenerationService._format_team(team_details)

        content = (
            f"{custom_prompt}\n\n"
            f"✨ Another milestone achieved!\n\n"
            f"Proud of our team: {team_names}\n\n"
            f"Key Highlights:\n"
            f"{RegenerationService._extract_highlights(case_study_text)}\n\n"
            f"#Leadership #Innovation #Teamwork"
        )

        return content.strip()

    # ==========================================================
    # LINKEDIN IMAGE PROMPT REGENERATION
    # ==========================================================

    @staticmethod
    def regenerate_linkedin_image_prompt(
        case_study_text: str,
        custom_prompt: str
    ) -> str:
        prompt = (
            f"{custom_prompt}\n\n"
            f"Create a modern LinkedIn post image that visually represents:\n"
            f"{RegenerationService._summarize_case_study(case_study_text)}\n\n"
            f"Style: Professional, corporate, clean layout, blue/white theme, "
            f"minimalistic, high-resolution, suitable for executive audience."
        )

        return prompt.strip()

    # ==========================================================
    # HELPERS
    # ==========================================================

    @staticmethod
    def _format_team(team: List[Dict[str, Any]]) -> str:
        if not team:
            return "Core Team"

        names = [member.get("name", "") for member in team if member.get("name")]
        return ", ".join(names) if names else "Core Team"

    @staticmethod
    def _extract_highlights(text: str) -> str:
        """
        Simple highlight extractor.
        Replace with NLP summarization later.
        """
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        return "\n".join(lines[:3]) if lines else "Successful transformation delivered."

    @staticmethod
    def _summarize_case_study(text: str) -> str:
        """
        Basic summarization logic placeholder.
        Replace with AI summarization later.
        """
        sentences = text.split(".")
        return sentences[0].strip() if sentences else "Business transformation initiative."