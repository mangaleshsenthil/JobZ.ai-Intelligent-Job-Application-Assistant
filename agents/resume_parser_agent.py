from services.gemini_service import generate_response
import json

class ResumeParserAgent:

    @staticmethod
    def parse_resume(resume_text: str):

        prompt = f"""
        Convert the following resume into structured JSON format.

        Structure:
        {{
            "name": "",
            "contact_info": {{
                "email": "",
                "phone": "",
                "linkedin": "",
                "github": ""
            }},
            "summary": "",
            "skills": [],
            "experience": [],
            "projects": [],
            "education": []
        }}

        Resume:
        {resume_text}
        """

        response = generate_response(prompt, is_json=True)
        
        return json.loads(response.strip())
