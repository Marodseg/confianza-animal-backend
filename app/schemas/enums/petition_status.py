from enum import Enum


class PetitionStatus(str, Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
