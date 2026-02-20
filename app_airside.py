import streamlit as st
import math
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="AirSide PRO", layout="wide")

st.title("🌀 AirSide PRO")
st.markdown("### Sistema Profissional de Dimensionamento Elétrico")
st.divider() 

CÁLCULO MOTOR

=====================================================

def calcular_motor(vazao, tensao, pressao_total=500, rendimento=0.65):
potencia_kw = (vazao * pressao_total) / (rendimento * 3600000)
potencia_kw *= 1.15
potencia_cv = potencia_kw / 0.736
potencia_motor = max(1, math.ceil(potencia_cv))

corrente = round((potencia_kw * 1000) / (math.sqrt(3) * tensao * 0.85), 2)  
disj_motor = math.ceil(corrente * 1.25)  
disj_geral = max(10, math.ceil(disj_motor * 1.3))  

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

=====================================================

MULTIFILAR MOTOR

=====================================================

def multifilar_motor(tipo_partida, tensao, motor, disj_geral):
if tipo_partida == "Inversor":
return f"Inversor {motor}CV conectado ao motor {motor}CV, DJ Geral {disj_geral}A\n"
elif tipo_partida == "Direta":
return f"Contator AC-3 e Relé Térmico conectado ao motor {motor}CV, DJ Geral {disj_geral}A\n"
elif tipo_partida == "Estrela-Triângulo":
return f"3 Contatores AC-3 + Temporizador Y-Δ conectado ao motor {motor}CV, DJ Geral {disj_geral}A\n"
elif tipo_partida == "Softstarter":
return f"Softstarter conectado ao motor {motor}CV, DJ Geral {disj_geral}A\n"
return ""

=====================================================

MULTIFILAR RESISTÊNCIA

=====================================================

def multifilar_resistencia(tensao, qtd, pot_unit, corrente_res):
return f"{qtd} Resistências {pot_unit}kW ligadas em {tensao}V, Corrente {corrente_res}A\n"

=====================================================

RESISTÊNCIA

=====================================================

def calcular_resistencia_por_potencia(pot_total, pot_unit, tensao):
qtd = math.ceil(pot_total / pot_unit)
corrente_res = round((pot_unit * 1000) / tensao, 2)
disj_res = math.ceil(corrente_res * 1.25)
return qtd, corrente_res, disj_res

def calcular_resistencia_por_quantidade(qtd, pot_unit, tensao):
corrente_res = round((pot_unit * 1000) / tensao, 2)
disj_res = math.ceil(corrente_res * 1.25)
return qtd, corrente_res, disj_res

=====================================================

ABAS

=====================================================

aba1, aba2, aba3, aba4, aba5 = st.tabs(
["📋 Dados", "📊 Resultado", "📑 Multifilar", "📦 Materiais", "🎛️ Simulador"]
)

=====================================================

ABA 1 - DADOS

=====================================================

with aba1:

col1, col2 = st.columns(2)  
cliente = col1.text_input("Nome do Cliente")  
tecnico = col2.text_input("Nome do Técnico")  

col3, col4, col5 = st.columns(3)  

tipo_partida = col3.selectbox(  
    "Tipo de Partida",  
    ["Inversor", "Direta", "Estrela-Triângulo", "Softstarter", "Somente Resistência"]  
)  

tensao = col4.selectbox("Tensão (V)", [220, 380, 440])  

if tipo_partida != "Somente Resistência":  
    vazao = col5.number_input("Vazão (m³/h)", value=5000.0)  
    pressao = st.number_input("Pressão Total (Pa)", min_value=100.0, value=500.0)  

st.divider()  
st.subheader("🔥 Resistência (Opcional)")  
usar_resistencia = st.checkbox("Adicionar Resistência")  

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

=====================================================

PROCESSAMENTO

=====================================================

if calcular:

motor_data = None  
res_data = None  

if tipo_partida != "Somente Resistência":  
    motor_data = calcular_motor(vazao, tensao, pressao)  

if usar_resistencia:  
    if modo_res == "Informar Potência Total":  
        res_data = calcular_resistencia_por_potencia(pot_total, pot_unit, tensao)  
    else:  
        res_data = calcular_resistencia_por_quantidade(qtd_res, pot_unit, tensao)  

st.session_state.update({  
    "motor": motor_data,  
    "res": res_data,  
    "tipo": tipo_partida,  
    "pot_unit": pot_unit if usar_resistencia else None  
})

=====================================================

ABA 2 - RESULTADO

=====================================================

with aba2:
if "motor" in st.session_state and st.session_state.motor:
motor, corrente, disj_motor, disj_geral, cabo = st.session_state.motor
st.metric("Motor (CV)", motor)
st.metric("Corrente (A)", corrente)
st.metric("DJ Motor (A)", disj_motor)
st.metric("DJ Geral (A)", disj_geral)
st.metric("Cabo (mm²)", cabo)

=====================================================

ABA 5 - SIMULADOR COMPLETO

=====================================================

with aba5:

st.subheader("🎛️ Simulador Industrial - Inversor + CLP")  

rpm_max = 3600  
setpoint = st.number_input("Pressão Alvo (Pa)", 100, 1000, 400)  
sujidade = st.slider("Sujidade do Filtro (%)", 0, 100, 0)  

if "rpm_auto" not in st.session_state:  
    st.session_state.rpm_auto = 1200  

rpm = st.session_state.rpm_auto  

pressao_motor = (rpm / rpm_max) * 500  
contrapressao = sujidade * 5  
pressao_total = pressao_motor + contrapressao  

erro = setpoint - pressao_total  
rpm += erro * 0.4  
rpm = max(0, min(rpm, rpm_max))  
st.session_state.rpm_auto = rpm  

pressao_total = round((rpm / rpm_max) * 500 + contrapressao, 1)  

st.divider()  

col1, col2, col3 = st.columns(3)  
col1.metric("RPM Atual", int(rpm))  
col2.metric("Pressão Total (Pa)", pressao_total)  
col3.metric("Erro", round(erro, 1))  

st.progress(rpm / rpm_max)  

st.divider()  

# PRESSOSTATOS  
p1_on = st.number_input("P1 Ativar (Pa)", 0, 2000, 700)  
p1_off = st.number_input("P1 Desativar (Pa)", 0, 2000, 600)  
p2_on = st.number_input("P2 Crítico (Pa)", 0, 2000, 900)  
p2_off = st.number_input("P2 Reset (Pa)", 0, 2000, 800)  

if "p1_estado" not in st.session_state:  
    st.session_state.p1_estado = False  
if "p2_estado" not in st.session_state:  
    st.session_state.p2_estado = False  

if pressao_total >= p1_on:  
    st.session_state.p1_estado = True  
elif pressao_total <= p1_off:  
    st.session_state.p1_estado = False  

if pressao_total >= p2_on:  
    st.session_state.p2_estado = True  
elif pressao_total <= p2_off:  
    st.session_state.p2_estado = False  

p1 = st.session_state.p1_estado  
p2 = st.session_state.p2_estado  

st.markdown(f"- Pressostato 1: {'🟡 Alarme' if p1 else '🟢 Normal'}")  
st.markdown(f"- Pressostato 2: {'🔴 Crítico' if p2 else '🟢 Normal'}")  

if p2:  
    st.error("🚨 Pressão Crítica! CLP Desligando Motor!")  
    st.session_state.rpm_auto = 0  
    rpm = 0  

st.divider()  
st.subheader("🌀 Motor")  

velocidade = max(0.2, 5 - (rpm / rpm_max) * 4.5)  

motor_html = f"""  
<div style="display:flex; justify-content:center;">  
    <div style="  
        width:150px;  
        height:150px;  
        border-radius:50%;  
        border:8px solid #1f77b4;  
        animation: spin {velocidade}s linear infinite;  
    "></div>  
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
