def inverter_setup(motor):

    return {
        "modo_controle": "V/F Quadrático",
        "frequencia_max": 60,
        "frequencia_min": 20,
        "rampa_subida": 15,
        "rampa_descida": 20,
        "corrente_motor": motor["nominal_current"],
        "limite_termico": motor["thermal_limit"],
        "sobrecorrente": round(motor["nominal_current"] * 1.2, 2)
    }
