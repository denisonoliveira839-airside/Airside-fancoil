def dimension_cable(current):

    tabela = [
        (10, 1.5),
        (16, 2.5),
        (25, 4),
        (32, 6),
        (40, 10),
        (63, 16),
        (80, 25),
        (100, 35),
        (125, 50)
    ]

    for limite, secao in tabela:
        if current <= limite:
            return secao

    return 70
