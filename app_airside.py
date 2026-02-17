import streamlit as st
import math
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="AirSide PRO 2.1", layout="wide")

st.title("🌀 AirSide PRO 2.1")
st.markdown("### Configurador e Gerador de Documentação Técnica HVAC")
st.divider()

# =====================================================
# FUNÇÕES DE CÁLCULO
# =====================================================

def calcular_motor(vazao, tensao, pressao_total):
    rendimento = 0.65
    potencia_kw = (vazao * pressao_total) / (rendimento * 3600000)
    potencia_kw *= 1.15

    potencia_cv = potencia_kw / 0.736
    motor_cv = max(1, math.ceil(potencia_cv))

    corrente = round((potencia_kw * 1000) / (math.sqrt(3) * tensao * 0.85), 2)

    disj_motor = math.ceil(corrente * 1.25)
    disj_geral = max(10, math.ceil(disj_motor * 1.3))

    return motor_cv, corrente, disj_motor, disj_geral


def calcular_resistencia_por_potencia(pot_total_kw, pot_unit_kw, tensao):
    quantidade = math.ceil(pot_total_kw / pot_unit_kw)
    corrente = round((pot_total_kw * 1000) / (math.sqrt(3) * tensao), 2)
    disj = math.ceil(corrente * 1.25)
    return quantidade, corrente, disj


def calcular_resistencia_por_quantidade(qtd, pot_unit_kw, tensao):
    pot_total = qtd * pot_unit_kw
    corrente = round((pot_total * 1000) / (math.sqrt(3) * tensao), 2)
    disj = math.ceil(corrente * 1.25)
    return pot_total, corrente, disj


# =====================================================
# MULTIFILARES
# =====================================================

def gerar_cabecalho(cliente, tecnico, tensao, tipo, vazao=None, pressao=None):
    data = datetime.now().strftime("%d/%m/%Y")

    texto = f"""
====================================================
               DOCUMENTAÇÃO TÉCNICA
====================================================

Cliente: {cliente}
Técnico Responsável: {tecnico}
Data: {data}

Tipo de Sistema: {tipo}
Tensão: {tensao}V
"""

    if vazao:
        texto += f"Vazão: {vazao} m³/h\n"
    if pressao:
        texto += f"Pressão Total: {pressao} Pa\n"

    texto += "\n====================================================\n"
    return texto


def multifilar_motor(tipo, tensao, motor, disj_geral):

    if tipo == "Inversor":
        return f"""
REDE {tensao}V → DJ Geral {disj_geral}A → Inversor → Motor {motor}CV
Saída U/V/W → Motor
"""

    elif tipo == "Direta":
        return f"""
REDE {tensao}V → DJ Geral {disj_geral}A → Contator → Relé Térmico → Motor {motor}CV
"""

    elif tipo == "Estrela-Triângulo":
        return f"""
REDE {tensao}V → DJ Geral {disj_geral}A
→ Contator Principal
→ Contator Estrela
→ Contator Triângulo
→ Temporizador Y-Δ
→ Motor {motor}CV
"""

    elif tipo == "Softstarter":
        return f"""
REDE {tensao}V → DJ Geral {disj_geral}A → Softstarter → Contator Bypass → Motor {motor}CV
"""

    else:
        return ""


def multifilar_resistencia(tensao, qtd, pot_unit, corrente):
    return f"""
REDE {tensao}V → DJ Resistência → Contator
Saída → {qtd} Resistências de {pot_unit} kW
Corrente Total: {corrente} A
Termostato de Segurança em Série
"""


# =====================================================
# INTERFACE
# =====================================================

aba1, aba2, aba3, aba4 = st.tabs(
    ["📋 Dados", "📊 Resultado", "📑 Multifilar", "📦 Materiais"]
)

with aba1:

    cliente = st.text_input("Cliente")
    tecnico = st.text_input("Técnico Responsável")

    st.divider()

    tipo_partida = st.selectbox(
        "Tipo de Sistema",
        ["Inversor", "Direta", "Estrela-Triângulo", "Softstarter", "Somente Resistência"]
    )

    tensao = st.selectbox("Tensão (V)", [220, 380, 440])

    if tipo_partida != "Somente Resistência":
        vazao = st.number_input("Vazão (m³/h)", value=5000.0)
        pressao = st.number_input("Pressão Total (Pa)", value=500.0)

    st.divider()
    st.subheader("🔥 Resistência (Opcional)")

    usar_resistencia = st.checkbox("Adicionar Resistência ao Sistema")

    if usar_resistencia:
        modo_res = st.radio(
            "Modo de Cálculo",
            ["Informar Potência Total", "Informar Quantidade"]
        )

        pot_unit = st.number_input("Potência Unitária (kW)", value=1.75)

        if modo_res == "Informar Potência Total":
            pot_total = st.number_input("Potência Total Desejada (kW)", value=10.5)
        else:
            qtd_res = st.number_input("Quantidade de Resistências", value=6)

    calcular = st.button("🔎 Gerar Projeto", use_container_width=True)


# =====================================================
# PROCESSAMENTO
# =====================================================

if calcular:

    motor_data = None
    res_data = None

    if tipo_partida != "Somente Resistência":
        motor_data = calcular_motor(vazao, tensao, pressao)

    if usar_resistencia:
        if modo_res == "Informar Potência Total":
            res_data = calcular_resistencia_por_potencia(
                pot_total, pot_unit, tensao
            )
        else:
            res_data = calcular_resistencia_por_quantidade(
                qtd_res, pot_unit, tensao
            )

    st.session_state.update({
        "cliente": cliente,
        "tecnico": tecnico,
        "tipo": tipo_partida,
        "tensao": tensao,
        "vazao": vazao if tipo_partida != "Somente Resistência" else None,
        "pressao": pressao if tipo_partida != "Somente Resistência" else None,
        "motor": motor_data,
        "res": res_data,
        "pot_unit": pot_unit if usar_resistencia else None
    })


# =====================================================
# RESULTADO
# =====================================================

with aba2:

    if "motor" in st.session_state and st.session_state.motor:

        motor, corrente, disj_motor, disj_geral = st.session_state.motor

        st.metric("Motor (CV)", motor)
        st.metric("Corrente (A)", corrente)
        st.metric("DJ Geral (A)", disj_geral)

    if "res" in st.session_state and st.session_state.res:

        res = st.session_state.res
        qtd = res[0]
        corrente_res = res[1]
        disj_res = res[2]

        st.metric("Qtd Resistências", qtd)
        st.metric("Corrente Resistência (A)", corrente_res)
        st.metric("DJ Resistência (A)", disj_res)


# =====================================================
# MULTIFILAR
# =====================================================

with aba3:

    if "tipo" in st.session_state:

        cabecalho = gerar_cabecalho(
            st.session_state.cliente,
            st.session_state.tecnico,
            st.session_state.tensao,
            st.session_state.tipo,
            st.session_state.vazao,
            st.session_state.pressao
        )

        texto = cabecalho

        if st.session_state.motor:
            motor, corrente, disj_motor, disj_geral = st.session_state.motor
            texto += multifilar_motor(
                st.session_state.tipo,
                st.session_state.tensao,
                motor,
                disj_geral
            )

        if st.session_state.res:
            qtd, corrente_res, disj_res = st.session_state.res
            texto += multifilar_resistencia(
                st.session_state.tensao,
                qtd,
                st.session_state.pot_unit,
                corrente_res
            )

        st.code(texto, language="text")


# =====================================================
# MATERIAIS
# =====================================================

with aba4:

    lista = []

    if "motor" in st.session_state and st.session_state.motor:
        motor, corrente, disj_motor, disj_geral = st.session_state.motor
        lista.append(("Disjuntor Geral", f"{disj_geral}A", "1 un"))
        lista.append(("Motor", f"{motor}CV", "1 un"))

        if st.session_state.tipo == "Inversor":
            lista.append(("Inversor", f"{motor}CV", "1 un"))
        elif st.session_state.tipo == "Direta":
            lista.append(("Contator", "AC-3", "1 un"))
            lista.append(("Relé Térmico", "Compatível", "1 un"))
        elif st.session_state.tipo == "Estrela-Triângulo":
            lista.append(("3 Contatores", "AC-3", "3 un"))
            lista.append(("Temporizador Y-Δ", "-", "1 un"))
        elif st.session_state.tipo == "Softstarter":
            lista.append(("Softstarter", f"{motor}CV", "1 un"))

    if "res" in st.session_state and st.session_state.res:
        qtd, corrente_res, disj_res = st.session_state.res
        lista.append(("Resistência", f"{st.session_state.pot_unit} kW", f"{qtd} un"))
        lista.append(("Disjuntor Resistência", f"{disj_res}A", "1 un"))

    if lista:
        df = pd.DataFrame(lista, columns=["Item", "Especificação", "Quantidade"])
        st.dataframe(df, use_container_width=True)
