# calculos.py
import math

def calcular_motor(vazao, tensao):
    """
    Calcula potência do motor, corrente, disjuntor e cabo
    """
    # Fórmula simplificada para dimensionamento de motor
    fator_seguranca = 1.25
    potencia_calc = vazao / 2649  # Ex.: m³/h para CV aproximado
    potencia_motor = math.ceil(potencia_calc * fator_seguranca / 1) * 1  # Arredonda para CV inteiro

    # Determinar tipo de partida
    if potencia_motor <= 5:
        partida = "Direta"
    else:
        partida = "Estrela-Triângulo"

    # Corrente aproximada
    if tensao == "220":
        corrente = round((potencia_motor * 746) / 220 * 1.1, 2)
    else:  # 380V
        corrente = round((potencia_motor * 746) / 380 * 1.1, 2)

    # Disjuntor e cabo
    disj_motor = round(corrente * 1.2)
    cabo_motor = 2.5 if corrente <= 20 else 4

    return potencia_motor, partida, corrente, disj_motor, cabo_motor

def calcular_disjuntor_cabo(potencia_banco, tensao):
    """
    Calcula corrente e disjuntor do banco de resistências
    """
    corrente = round((potencia_banco * 1000) / int(tensao), 2)
    disj_banco = round(corrente * 1.2)
    return corrente, disj_banco
