# agents/role_detection_agent.py
#
# Instead of calling Gemini, we derive search keywords directly from the
# parsed resume (skills + experience titles). This avoids an extra API call
# and ensures the job search reflects what's actually IN the resume.

import re


def _normalise(text: str) -> str:
    """Lowercase & strip punctuation for comparison."""
    return re.sub(r"[^a-z0-9 ]", "", text.lower()).strip()


class RoleDetectionAgent:

    @staticmethod
    def detect_role(resume_json: dict) -> str:
        """
        Returns a comma-separated string of relevant job-search keywords
        derived entirely from the resume – no external AI call required.

        Priority order:
          1. Explicit skills listed on the resume
          2. Job titles from past experience
          3. Project technology stack keywords
        """
        keywords: list[str] = []
        seen: set[str] = set()

        def add(term: str):
            norm = _normalise(term)
            if norm and norm not in seen and len(norm) > 1:
                seen.add(norm)
                keywords.append(term.strip())

        # ── 1. Skills ─────────────────────────────────────────────────────
        for skill in resume_json.get("skills", []):
            if isinstance(skill, str):
                add(skill)
            elif isinstance(skill, dict):
                # Handle {name: ..., level: ...} style entries
                add(str(skill.get("name", "") or skill.get("skill", "")))

        # ── 2. Previous job titles ────────────────────────────────────────
        for exp in resume_json.get("experience", []):
            if isinstance(exp, dict):
                title = exp.get("title", "") or exp.get("position", "") or exp.get("role", "")
                if title:
                    add(title)

        # ── 3. Project tech keywords ──────────────────────────────────────
        for project in resume_json.get("projects", []):
            if isinstance(project, dict):
                tech_list = project.get("technologies", []) or project.get("tech_stack", [])
                for tech in tech_list:
                    if isinstance(tech, str):
                        add(tech)

        # ── De-duplicate and return top 10 ────────────────────────────────
        return ", ".join(keywords[:10]) if keywords else "Software Engineer"