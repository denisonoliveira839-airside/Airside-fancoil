def validate_system(status):

    if status["emergencia"]:
        return "BLOQUEADO_TOTAL"

    if not status["fluxo_ok"]:
        return "BLOQUEAR_RESISTENCIA"

    if status["filtro_sujo"]:
        return "ALARME_FILTRO"

    return "SISTEMA_OK"
