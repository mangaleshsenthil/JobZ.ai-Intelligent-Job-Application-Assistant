import re
from services.embedding_service import compute_similarity

class JobScorerAgent:

    @staticmethod
    def _normalise(text: str) -> str:
        return re.sub(r"[^a-z0-9 ]", "", text.lower()).strip()

    @staticmethod
    def score_jobs(resume_json, jobs):
        """
        Calculates an extremely lenient, high-value hybrid scoring system:
        - Keyword Presence (40%): Focused on 'is this a match at all?'.
        - Semantic Similarity (60%): Deep contextual matching.
        - Extreme Lenience: We lower the bar for what counts as 'full match'.
        """
        
        # ── 1. Preparation: Extract Core Resume Keywords ────────────
        skills = [s.strip().lower() for s in resume_json.get("skills", []) if isinstance(s, str)]
        
        roles = []
        for exp in resume_json.get("experience", []):
            title = exp.get("title", "").lower()
            if title:
                roles.extend([w for w in title.split() if len(w) > 3])
                roles.append(title)
        
        core_keywords = set(skills + roles)
        core_keywords = {k for k in core_keywords if len(k) > 2}
        
        # Weighted Blob for Semantic Match
        summary = resume_json.get("summary", "")
        skills_str = ", ".join(skills)
        experiences_str = " ".join([exp.get("title", "") for exp in resume_json.get("experience", []) if isinstance(exp, dict)])
        resume_blob = f"{skills_str} {skills_str} {summary} {experiences_str}".strip()
        
        scored_jobs = []
        for job in jobs:
            job_title = job.get("title", "").lower()
            job_desc = job.get("description", "").lower()
            job_blob = f"{job_title} {job_desc}"
            
            # --- A. Keyword Presence Score (EXTREME LENIENCE) ---
            # Instead of dividing by ALL keywords, we divide by a target number (8).
            # If a candidate matches 8 skills/roles, that's a 'perfect' match for a description.
            matches = sum(1 for kw in core_keywords if kw in job_blob)
            target_matches = min(len(core_keywords), 8) # We only look for top 8 matches
            keyword_score = (matches / max(target_matches, 1))
            keyword_score = min(keyword_score, 1.0)
            
            # --- B. Semantic Similarity ---
            semantic_score = compute_similarity(resume_blob, job_desc)
            
            # --- C. Final Hybrid Calculation with Balanced Floor ---
            # We use a 25% floor. This allows truly unrelated jobs to stay low,
            # but pushes 'growth' roles (partial matches) into the 50-60% range.
            base_floor = 0.25
            
            # Weighted logic (0.0 to 1.0)
            weighted_logic = (keyword_score * 0.45) + (min(semantic_score, 1.0) * 0.55)
            
            # Scale the logic to the remaining 75% range
            final_score = base_floor + (weighted_logic * 0.75)
            
            # Boost: Title Match (direct role keyword in title)
            # We only give this boost if they already have a decent base (>40%)
            if final_score > 0.35:
                if any(role_kw in job_title for role_kw in ["analyst", "data", "engineer", "scientist"]):
                    if any(role_kw in resume_blob.lower() for role_kw in ["analyst", "data", "engineer", "scientist"]):
                        final_score += 0.12 # 12% nudge for role alignment
            
            # Final touch: Cap at 100%, convert to percentage
            final_percentage = min(final_score, 1.0) * 100
            
            # If it's a very low score, we don't want to show 35% if it's truly bad.
            # But the discovery agent already filters out 0-match jobs.
            
            job["score"] = round(final_percentage, 1)
            scored_jobs.append(job)

        return sorted(scored_jobs, key=lambda x: x["score"], reverse=True)
