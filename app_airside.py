import streamlit as st
import math
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt

st.set_page_config(page_title="AirSide PRO", layout="wide")
st.title("🌀 AirSide PRO - Sistema Profissional de Dimensionamento Elétrico")
st.divider()

# =====================================================
# FUNÇÕES DE CÁLCULO
# =====================================================
def calcular_motor(vazao, tensao, pressao_total=500, rendimento=0.65):
    potencia_kw = (vazao * pressao_total) / (rendimento * 3600000)
    potencia_kw *= 1.15
    potencia_cv = potencia_kw / 0.736
    potencia_motor = max(1, math.ceil(potencia_cv))
    corrente = round((potencia_kw*1000)/(math.sqrt(3)*tensao*0.85),2)
    disj_motor = math.ceil(corrente*1.25)
    disj_geral = max(10, math.ceil(disj_motor*1.3))
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

def calcular_resistencia_por_potencia(pot_total, pot_unit, tensao):
    qtd = math.ceil(pot_total / pot_unit)
    corrente_unit = round((pot_unit*1000)/tensao,2)
    corrente_total = round(corrente_unit*qtd,2)
    disj_res = math.ceil(corrente_total*1.25)
    return qtd, corrente_total, disj_res

def calcular_resistencia_por_quantidade(qtd, pot_unit, tensao):
    corrente_unit = round((pot_unit*1000)/tensao,2)
    corrente_total = round(corrente_unit*qtd,2)
    disj_res = math.ceil(corrente_total*1.25)
    return qtd, corrente_total, disj_res

def gerar_cabecalho(cliente, tecnico, tensao, tipo, vazao=None, pressao=None):
    data = datetime.now().strftime("%d/%m/%Y")
    texto = f"Cliente: {cliente}\nTécnico: {tecnico}\nData: {data}\nTensão: {tensao}V\nTipo de Partida: {tipo}"
    if vazao:
        texto += f"\nVazão: {vazao} m³/h"
    if pressao:
        texto += f"\nPressão Total: {pressao} Pa"
    return texto+"\n"+"="*50+"\n"

def multifilar_motor(tipo, tensao, motor, disj_geral):
    if tipo=="Inversor":
        return f"\n--- Multifilar Motor (Inversor) ---\nL1/L2/L3 → Disj Geral {disj_geral}A → Inversor → Motor {motor}CV\n"
    elif tipo=="Direta":
        return f"\n--- Multifilar Motor (Partida Direta) ---\nL1/L2/L3 → Disj Geral {disj_geral}A → Contator → Motor {motor}CV\n"
    elif tipo=="Estrela-Triângulo":
        return f"\n--- Multifilar Motor (Estrela-Triângulo) ---\nL1/L2/L3 → Disj Geral {disj_geral}A → 3 Contatores → Motor {motor}CV\n"
    elif tipo=="Softstarter":
        return f"\n--- Multifilar Motor (Softstarter) ---\nL1/L2/L3 → Disj Geral {disj_geral}A → Softstarter → Motor {motor}CV\n"
    else:
        return ""

def multifilar_resistencia(tensao, qtd, pot_unit, corrente_total):
    return f"\n--- Multifilar Resistências ---\nL1/L2 → Disj Resistência → {qtd}x Resistências {pot_unit}kW → Total Corrente: {corrente_total}A\n"

# =====================================================
# ABAS
# =====================================================
aba1, aba2, aba3, aba4, aba5 = st.tabs(
    ["📋 Dados", "📊 Resultado", "📑 Multifilar", "📦 Materiais", "🎛️ Simulador"]
)

# =====================================================
# ABA 1 - DADOS
# =====================================================
with aba1:
    col1, col2 = st.columns(2)
    cliente = col1.text_input("Nome do Cliente")
    tecnico = col2.text_input("Nome do Técnico")

    st.divider()
    tipo_partida = st.selectbox(
        "Tipo de Partida",
        ["Inversor", "Direta", "Estrela-Triângulo", "Softstarter", "Somente Resistência"]
    )
    tensao = st.selectbox("Tensão (V)", [220, 380, 440])

    if tipo_partida != "Somente Resistência":
        vazao = st.number_input("Vazão (m³/h)", value=5000.0)
        pressao = st.number_input("Pressão Total (Pa)", value=500.0)
    else:
        vazao = None
        pressao = None

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
            res_data = calcular_resistencia_por_potencia(pot_total, pot_unit, tensao)
        else:
            res_data = calcular_resistencia_por_quantidade(qtd_res, pot_unit, tensao)
    st.session_state.update({
        "cliente": cliente,
        "tecnico": tecnico,
        "tipo": tipo_partida,
        "tensao": tensao,
        "vazao": vazao,
        "pressao": pressao,
        "motor": motor_data,
        "res": res_data,
        "pot_unit": pot_unit if usar_resistencia else None
    })

# =====================================================
# ABA 2 - RESULTADO
# =====================================================
with aba2:
    if "motor" in st.session_state and st.session_state.motor:
        motor, corrente, disj_motor, disj_geral, cabo = st.session_state.motor
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Motor (CV)", motor)
        col2.metric("Corrente (A)", corrente)
        col3.metric("DJ Motor (A)", disj_motor)
        col4.metric("DJ Geral (A)", disj_geral)
        col5.metric("Cabo (mm²)", cabo)

    if "res" in st.session_state and st.session_state.res:
        qtd, corrente_res, disj_res = st.session_state.res
        col1, col2, col3 = st.columns(3)
        col1.metric("Qtd Resistências", qtd)
        col2.metric("Corrente Resistência (A)", corrente_res)
        col3.metric("DJ Resistência (A)", disj_res)

# =====================================================
# ABA 3 - MULTIFILAR
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
            motor, corrente, disj_motor, disj_geral, cabo = st.session_state.motor
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
# ABA 4 - MATERIAIS
# =====================================================
with aba4:
    lista = []
    if "motor" in st.session_state and st.session_state.motor:
        motor, corrente, disj_motor, disj_geral, cabo = st.session_state.motor
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
        st.download_button(
            "⬇ Exportar Lista em CSV",
            df.to_csv(index=False),
            file_name="lista_materiais.csv",
            mime="text/csv"
        )

# =====================================================
# ABA 5 - SIMULADOR PRESSOSTATO / VENTILADOR
# =====================================================
with aba5:
    st.subheader("💨 Simulação de Pressostatos e Ventilador")
    filtro_sujo = st.slider("Nível de Sujidade do Filtro (%)", 0, 100, 0)
    pressostato1_set = st.number_input("Pressostato 1 Atuação (%)", value=70)
    pressostato2_set = st.number_input("Pressostato 2 Atuação (%)", value=90)

    ventilador_ligado = filtro_sujo < pressostato1_set
    pressostato1_ativo = filtro_sujo >= pressostato1_set
    pressostato2_ativo = filtro_sujo >= pressostato2_set

    st.markdown("### 🔹 Status Atual")
    st.write(f"- Ventilador: {'🟢 Ligado' if ventilador_ligado else '🔴 Desligado'}")
    st.write(f"- Pressostato 1: {'🔴 Desligado' if not pressostato1_ativo else '🟢 Ativo'}")
    st.write(f"- Pressostato 2: {'🔴 Desligado' if not pressostato2_ativo else '🟢 Ativo'}")

    if not ventilador_ligado:
        st.warning("⚠️ Ventilador desligado devido à pressão alta no filtro!")

    x = np.arange(0, 101, 1)
    y1 = x >= pressostato1_set
    y2 = x >= pressostato2_set
    y_vent = x < pressostato1_set

    fig, ax = plt.subplots()
    ax.plot(x, y_vent, label="Ventilador Ligado", color="green")
    ax.plot(x, y1, label="Pressostato 1 Ativo", color="orange")
    ax.plot(x, y2, label="Pressostato 2 Ativo", color="red")
    ax.set_xlabel("Sujidade do Filtro (%)")
    ax.set_ylabel("Estado (0=Desligado, 1=Ativo)")
    ax.set_yticks([0,1])
    ax.set_yticklabels(["Desligado","Ativo"])
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)
