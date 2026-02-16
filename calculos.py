# calculos.py
import math

def calcular_motor(vazao, tensao, pressao_total=500, rendimento=0.65):
    """
    Dimensionamento técnico de motor para ventilador (Fancoil)

    vazao: m³/h
    tensao: "220" ou "380"
    pressao_total: Pa (default 500 Pa típico Fancoil)
    rendimento: eficiência do conjunto ventilador
    """

    # =============================
    # POTÊNCIA REAL (kW)
    # =============================

    potencia_kw = (vazao * pressao_total) / (rendimento * 3600000)

    # Margem técnica 15%
    potencia_kw *= 1.15

    # Converter para CV
    potencia_cv = potencia_kw / 0.736

    # Arredondar para motor comercial inteiro
    potencia_motor = math.ceil(potencia_cv)

    # =============================
    # TIPO DE PARTIDA
    # =============================

    if potencia_motor <= 5:
        partida = "Direta"
    elif potencia_motor <= 15:
        partida = "Estrela-Triângulo"
    else:
        partida = "Soft-Starter ou Inversor"

    # =============================
    # CORRENTE TRIFÁSICA REAL
    # =============================

    tensao_int = int(tensao)

    corrente = round(
        (potencia_kw * 1000) / (math.sqrt(3) * tensao_int * 0.85),
        2
    )

    # =============================
    # DISJUNTOR
    # =============================

    disj_motor = math.ceil(corrente * 1.25)

    # =============================
    # CABO (tabela simplificada)
    # =============================

    if corrente <= 18:
        cabo_motor = 2.5
    elif corrente <= 28:
        cabo_motor = 4
    elif corrente <= 36:
        cabo_motor = 6
    elif corrente <= 50:
        cabo_motor = 10
    else:
        cabo_motor = 16

    return potencia_motor, partida, corrente, disj_motor, cabo_motor


def calcular_disjuntor_cabo(potencia_banco, tensao):
    """
    Banco de resistência trifásico
    """

    tensao_int = int(tensao)

    corrente = round(
        (potencia_banco * 1000) / (math.sqrt(3) * tensao_int),
        2
    )

    disj_banco = math.ceil(corrente * 1.25)

    return corrente, disj_banco
