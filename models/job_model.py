# models/job_model.py

from dataclasses import dataclass

@dataclass
class Job:
    title: str
    company: str
    location: str
    description: str
    url: str = ""
    score: float = 0.0