def filter_threshold(tipo_filtro):

    valores = {
        "Leve": 150,
        "Médio": 250,
        "Pesado": 400
    }

    return valores.get(tipo_filtro, 250)
