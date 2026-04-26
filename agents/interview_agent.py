# agents/interview_agent.py

from services.gemini_service import generate_response
import json

class InterviewAgent:

    @staticmethod
    def generate_guidance(resume_json, job_description):
        prompt = f"""
        You are an expert career and interview coach.
        
        Using the tailored resume provided, and the job description, generate 3-4 highly personalized application or interview questions the candidate might be asked for this specific role.

        For each question, provide a solid, confident 2-3 sentence answer pulling DIRECTLY from the experiences and skills in the candidate's resume so they can sound like a perfect fit.

        Structure your output as exactly this JSON format:
        [
            {{
                "question": "What is the question?",
                "answer": "Here is the customized answer..."
            }}
        ]

        Resume:
        {json.dumps(resume_json)}

        Job Description:
        {job_description}
        """

        response = generate_response(prompt, is_json=True)
        return json.loads(response.strip())
