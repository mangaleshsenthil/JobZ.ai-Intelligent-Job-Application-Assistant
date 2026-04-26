# models/resume_model.py

from dataclasses import dataclass
from typing import List

@dataclass
class Project:
    title: str
    description: str

@dataclass
class Resume:
    name: str
    summary: str
    skills: List[str]
    projects: List[Project]