# agents/application_agent.py

from services.pdf_service import PDFService
from agents.memory_agent import MemoryAgent
import os

class ApplicationAgent:

    @staticmethod
    def apply(job, tailored_resume_json):

        output_path = f"data/resumes/{job['title']}_tailored.pdf"

        PDFService.generate_resume_pdf(tailored_resume_json, output_path)

        MemoryAgent.store_application(job, job["score"])

        return output_path