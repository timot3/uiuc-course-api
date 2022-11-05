from dataclasses import dataclass
import json


@dataclass
class Course:
    name: str  # "CS 124"
    number: str  # "124"
    label: str  # "Introduction to Computer Science I"
    description: str  # "Basic concepts in computing and fundamental techniques for solving computational problems..."
    GPA: str  # "No Data"
    hours: str  # "3"
