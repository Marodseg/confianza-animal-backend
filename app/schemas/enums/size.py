from enum import Enum


class Size(str, Enum):
    mini = "mini"
    small = "pequeño"
    medium = "mediano"
    large = "grande"
    extra_large = "gigante"
