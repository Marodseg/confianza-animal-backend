from enum import Enum


class PetitionStatus(str, Enum):
    initiated = "Iniciada"
    info_pending = "Información pendiente de revisión"
    info_approved = "Pendiente de documentación"
    docu_envied = "Documentación enviada"
    docu_pending = "Documentación pendiente de revisión"
    info_rejected = "Información rechazada"
    info_changed = "Información modificada"
    docu_rejected = "Documentación rechazada"
    docu_changed = "Documentación modificada"
    accepted = "Solicitud aceptada"
    rejected = "Solicitud rechazada"
