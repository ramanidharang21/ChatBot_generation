from typing import Dict, Any, List


class GenerationService:
    """
    Handles all text and content generation logic
    for Case Study and LinkedIn artifacts.
    """

    # ==========================================================
    # CASE STUDY GENERATION
    # ==========================================================

    @staticmethod
    def generate_case_study(metadata: Dict[str, Any]) -> str:
        team_names = GenerationService._format_team(metadata.get("team", []))

        content = f"""
About the Company:
{metadata['brand']} operates in the {metadata['domain']} industry.

Project Overview:
The project "{metadata['project_name']}" was executed between 
{metadata['start_date']} and {metadata['end_date']}.

Business Challenge:
The organization faced operational inefficiencies and scalability challenges.

Solution Delivered:
A strategic and technology-driven implementation was executed by the team: {team_names}.

Impact & Outcome:
The engagement resulted in measurable performance improvements, optimized workflows,
and enhanced business agility.
"""

        return content.strip()

    # ==========================================================
    # CASE STUDY REGENERATION
    # ==========================================================

    @staticmethod
    def regenerate_case_study(metadata: Dict[str, Any], custom_prompt: str) -> str:
        team_names = GenerationService._format_team(metadata.get("team", []))

        enhanced_content = f"""
{custom_prompt}

Enhanced Case Study for "{metadata['project_name']}":

Led by {team_names}, the engagement transformed operational efficiency,
strengthened digital capabilities, and delivered measurable ROI.
"""

        return enhanced_content.strip()

    # ==========================================================
    # LINKEDIN TEXT GENERATION
    # ==========================================================

    @staticmethod
    def generate_linkedin_text(metadata: Dict[str, Any]) -> str:
        team_names = GenerationService._format_team(metadata.get("team", []))

        content = (
            f"🚀 Successfully delivered '{metadata['project_name']}'!\n\n"
            f"Proud to collaborate with an incredible team: {team_names}.\n\n"
            f"This initiative enhanced performance, streamlined processes, "
            f"and created lasting business impact.\n\n"
            f"#DigitalTransformation #{metadata['domain']} #TeamSuccess"
        )

        return content

    # ==========================================================
    # LINKEDIN TEXT REGENERATION
    # ==========================================================

    @staticmethod
    def regenerate_linkedin_text(custom_prompt: str) -> str:
        enhanced = (
            f"{custom_prompt}\n\n"
            f"Delivering excellence through collaboration and innovation. 🚀"
        )
        return enhanced

    # ==========================================================
    # LINKEDIN IMAGE PLACEHOLDER
    # ==========================================================

    @staticmethod
    def generate_linkedin_image_bytes() -> bytes:
        """
        Placeholder for image generation logic.
        Replace with AI image generation or Canva API integration later.
        """
        return b"LinkedIn Image Binary Placeholder"

    @staticmethod
    def regenerate_linkedin_image_bytes() -> bytes:
        return b"Regenerated LinkedIn Image Binary"

    # ==========================================================
    # HELPER
    # ==========================================================

    @staticmethod
    def _format_team(team: List[Dict[str, Any]]) -> str:
        if not team:
            return "Core Project Team"

        names = [member.get("name", "") for member in team if member.get("name")]
        return ", ".join(names) if names else "Core Project Team"