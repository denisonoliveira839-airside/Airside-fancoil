def generate_clp_logic(equipment):

    logica = {
        "verifica_emergencia": True,
        "verifica_porta": True,
        "aciona_ventilador": True,
        "confirma_fluxo": True,
        "delay_resistencia": 5,
        "monitor_filtro": True,
        "alarme_visual": True
    }

    if equipment == "Banco Resistência":
        logica["acionamento_sequencial"] = True

    return logica
