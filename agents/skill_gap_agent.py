# agents/skill_gap_agent.py

from services.gemini_service import generate_response
import json
import requests

class SkillGapAgent:

    @staticmethod
    def _is_link_valid(url):
        """Checks if a URL is reachable and returns a successful status code."""
        try:
            # Use HEAD request for speed and a short timeout
            response = requests.head(url, timeout=3, allow_redirects=True)
            return response.status_code < 400
        except Exception:
            try:
                # Some sites block HEAD requests, try a small GET as fallback
                response = requests.get(url, timeout=3, stream=True)
                return response.status_code < 400
            except Exception:
                return False

    @staticmethod
    def analyze_gap(resume_json, job_description):
        """
        Identifies missing skills and suggests valid study materials.
        Validates all links before returning them.
        """
        
        prompt = f"""
        You are a career development expert. Compare the provided candidate resume JSON with the job description.
        
        1. Identify the top 3-4 CRITICAL technical skills or tools that are required by the job but MISSING or WEAK in the resume.
        2. For each missing skill, provide:
           - A brief explanation of why it's important for this role.
           - 1-2 specific, valid study material links (e.g., official documentation, GitHub repositories, tutorials, or high-quality articles). 
           - PRIORITIZE stable, evergreen URLs (like top-level documentation) over deep-links that may break.
           - DO NOT suggest generic paid courses if official documentation or free study materials are available.
        
        STRICTLY return the response as a JSON array of objects with the following structure:
        [
          {{
            "skill": "Skill Name",
            "suggestion": "Why it's important and what to focus on...",
            "links": [
              {{"title": "Documentation/Tutorial Title", "url": "https://..."}}
            ]
          }}
        ]
        
        If the resume is already a perfect match, return an empty array [].
        
        Resume JSON:
        {json.dumps(resume_json)}
        
        Job Description:
        {job_description}
        """

        try:
            response = generate_response(prompt, is_json=True)
            gaps = json.loads(response.strip())
            
            # Post-process: Validate every link
            validated_gaps = []
            for item in gaps:
                valid_links = []
                for link in item.get("links", []):
                    url = link.get("url")
                    if url and SkillGapAgent._is_link_valid(url):
                        valid_links.append(link)
                
                # Only include the skill if it has at least one valid link
                if valid_links:
                    item["links"] = valid_links
                    validated_gaps.append(item)
            
            return validated_gaps
        except Exception as e:
            print(f"Error in SkillGapAgent: {e}")
            return []
