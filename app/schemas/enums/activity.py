from enum import Enum


class Activity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
