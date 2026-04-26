# models/application_model.py

from dataclasses import dataclass
from datetime import datetime

@dataclass
class Application:
    job_title: str
    company: str
    score: float
    applied_on: datetime