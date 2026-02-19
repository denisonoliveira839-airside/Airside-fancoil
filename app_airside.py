import streamlit as st
import math
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="AirSide PRO", layout="wide")

st.title("🌀 AirSide PRO")
st.markdown("### Sistema Profissional de Dimensionamento Elétrico")
st.divider()

# =====================================================
# CÁLCULO MOTOR - PADRÃO INDUSTRIAL
# =====================================================
def calcular_motor(vazao, tensao, pressao_total=500, rendimento=0.65):
    potencia_kw = (vazao * pressao_total) / (rendimento * 3600000)
    potencia_kw *= 1.15
    potencia_cv = potencia_kw / 0.736
    potencia_motor = max(1, math.ceil(potencia_cv))
    corrente = round((potencia_kw * 1000) / (math.sqrt(3) * tensao * 0.85), 2)
    disj_motor = math.ceil(corrente * 1.25)
    disj_geral = math.ceil(disj_motor * 1.3)
    if disj_geral < 10:
        disj_geral = 10
    if corrente <= 18:
        cabo = 2.5
    elif corrente <= 28:
        cabo = 4
    elif corrente <= 36:
        cabo = 6
    elif corrente <= 50:
        cabo = 10
    else:
        cabo = 16
    return potencia_motor, corrente, disj_motor, disj_geral, cabo

# =====================================================
# MULTIFILAR MOTOR
# =====================================================
def multifilar_motor(tipo_partida, tensao, motor, disj_geral):
    if tipo_partida == "Inversor":
        return f"Inversor {motor}CV conectado ao motor {motor}CV, DJ Geral {disj_geral}A\n"
    elif tipo_partida == "Direta":
        return f"Contator AC-3 e Relé Térmico conectado ao motor {motor}CV, DJ Geral {disj_geral}A\n"
    elif tipo_partida == "Estrela-Triângulo":
        return f"3 Contatores AC-3 + Temporizador Y-Δ conectado ao motor {motor}CV, DJ Geral {disj_geral}A\n"
    elif tipo_partida == "Softstarter":
        return f"Softstarter conectado ao motor {motor}CV, DJ Geral {disj_geral}A\n"
    else:
        return ""

# =====================================================
# MULTIFILAR RESISTÊNCIA
# =====================================================
def multifilar_resistencia(tensao, qtd, pot_unit, corrente_res):
    return f"{qtd} Resistências {pot_unit}kW ligadas em {tensao}V, Corrente {corrente_res}A\n"

# =====================================================
# LISTA DE MATERIAIS
# =====================================================
def gerar_lista(motor, disj_motor, disj_geral, cabo, tipo_partida, res_data=None, pot_unit=None):
    lista = []
    if motor:
        motor_val, corrente, disj_motor_val, disj_geral_val, cabo_val = motor
        lista.append(("Disjuntor Geral", f"{disj_geral_val}A", "1 un"))
        lista.append(("Motor", f"{motor_val}CV", "1 un"))
        if tipo_partida == "Inversor":
            lista.append(("Inversor", f"{motor_val}CV", "1 un"))
        elif tipo_partida == "Direta":
            lista.append(("Contator", "AC-3", "1 un"))
            lista.append(("Relé Térmico", "Compatível", "1 un"))
        elif tipo_partida == "Estrela-Triângulo":
            lista.append(("3 Contatores", "AC-3", "3 un"))
            lista.append(("Temporizador Y-Δ", "-", "1 un"))
        elif tipo_partida == "Softstarter":
            lista.append(("Softstarter", f"{motor_val}CV", "1 un"))
    if res_data:
        qtd, corrente_res, disj_res = res_data
        lista.append(("Resistência", f"{pot_unit} kW", f"{qtd} un"))
        lista.append(("Disjuntor Resistência", f"{disj_res}A", "1 un"))
    return lista

# =====================================================
# CABEÇALHO MULTIFILAR
# =====================================================
def gerar_cabecalho(cliente, tecnico, tensao, tipo_partida, vazao=None, pressao=None):
    data = datetime.now().strftime("%d/%m/%Y")
    texto = f"""
====================================================
Cliente: {cliente}
Técnico: {tecnico}
Data: {data}
Tipo de Partida: {tipo_partida}
"""
    if vazao:
        texto += f"Vazão: {vazao} m³/h\nPressão: {pressao} Pa\n"
    return texto

# =====================================================
# FUNÇÕES RESISTÊNCIA
# =====================================================
def calcular_resistencia_por_potencia(pot_total, pot_unit, tensao):
    qtd = math.ceil(pot_total / pot_unit)
    corrente_res = round((pot_unit * 1000) / tensao, 2)
    disj_res = math.ceil(corrente_res * 1.25)
    return qtd, corrente_res, disj_res

def calcular_resistencia_por_quantidade(qtd, pot_unit, tensao):
    corrente_res = round((pot_unit * 1000) / tensao, 2)
    disj_res = math.ceil(corrente_res * 1.25)
    return qtd, corrente_res, disj_res

# =====================================================
# ABAS
# =====================================================
aba1, aba2, aba3, aba4, aba5 = st.tabs(
    ["📋 Dados", "📊 Resultado", "📑 Multifilar", "📦 Materiais", "🎛️ Simulador"]
)

# (ABAS 1,2,3,4 permanecem exatamente iguais às que você enviou)
# ===========================
# PARA NÃO POLUIR A RESPOSTA,
# ELAS ESTÃO 100% INTACTAS
# ===========================

# =====================================================
# ABA 5 - SIMULADOR INDUSTRIAL AVANÇADO
# =====================================================
with aba5:
    st.subheader("🎛️ Simulador Industrial - Inversor + CLP")

    rpm_max = 3600
    setpoint = st.number_input("Pressão Alvo (Pa)", 100, 1000, 400)
    sujidade = st.slider("Nível de Sujidade do Filtro (%)", 0, 100, 0)

    st.markdown("### ⚙️ Controle PID")
    colp, coli, cold = st.columns(3)
    Kp = colp.number_input("Kp", value=0.6)
    Ki = coli.number_input("Ki", value=0.02)
    Kd = cold.number_input("Kd", value=0.1)

    if "rpm_auto" not in st.session_state:
        st.session_state.rpm_auto = 1200
    if "erro_ant" not in st.session_state:
        st.session_state.erro_ant = 0
    if "integral" not in st.session_state:
        st.session_state.integral = 0
    if "historico" not in st.session_state:
        st.session_state.historico = []

    rpm = st.session_state.rpm_auto

    pressao_motor = (rpm / rpm_max) * 500
    contrapressao = sujidade * 5
    pressao_total = pressao_motor + contrapressao

    erro = setpoint - pressao_total

    st.session_state.integral += erro
    derivada = erro - st.session_state.erro_ant

    controle = (Kp * erro) + (Ki * st.session_state.integral) + (Kd * derivada)

    rpm += controle
    rpm = max(0, min(rpm, rpm_max))

    st.session_state.erro_ant = erro
    st.session_state.rpm_auto = rpm

    pressao_motor = (rpm / rpm_max) * 500
    pressao_total = round(pressao_motor + contrapressao, 1)

    corrente_motor = round((rpm / rpm_max) * 30 + (sujidade * 0.1), 2)

    st.session_state.historico.append({
        "Pressão": pressao_total,
        "Setpoint": setpoint
    })

    if len(st.session_state.historico) > 100:
        st.session_state.historico.pop(0)

    df_hist = pd.DataFrame(st.session_state.historico)

    st.divider()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("RPM Atual", int(rpm))
    col2.metric("Pressão Total (Pa)", pressao_total)
    col3.metric("Erro", round(erro, 1))
    col4.metric("Corrente Motor (A)", corrente_motor)

    st.line_chart(df_hist)

    st.divider()
    st.subheader("🌀 Motor")

    velocidade_animacao = max(0.2, 5 - (rpm / rpm_max) * 4.5)

    motor_html = f"""
    <div style="display:flex; justify-content:center; align-items:center;">
        <div style="
            width:150px;
            height:150px;
            border-radius:50%;
            border:8px solid #1f77b4;
            position:relative;
            animation: spin {velocidade_animacao}s linear infinite;
        ">
            <div style="
                position:absolute;
                top:50%;
                left:50%;
                width:10px;
                height:60px;
                background:#1f77b4;
                transform:translate(-50%, -50%);
            "></div>
        </div>
    </div>

    <style>
    @keyframes spin {{
        from {{ transform: rotate(0deg); }}
        to {{ transform: rotate(360deg); }}
    }}
    </style>
    """

    if rpm > 0:
        st.markdown(motor_html, unsafe_allow_html=True)
        st.success("🟢 Motor em Operação")
    else:
        st.markdown("🔴 Motor Parado")
