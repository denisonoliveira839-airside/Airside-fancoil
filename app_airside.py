
import streamlit as st
import math
from datetime import datetime

st.set_page_config(page_title="AirSide PRO", layout="wide")

st.title("🌀 AirSide PRO")
st.subheader("Sistema Profissional de Dimensionamento Elétrico")
st.divider()

# =====================================================
# FUNÇÕES
# =====================================================

def calcular_motor(vazao, tensao, pressao):
    potencia_w = (vazao * pressao) / 3600
    potencia_cv = potencia_w / 735.5
    corrente = potencia_w / (math.sqrt(3) * tensao * 0.85)

    return {
        "potencia_w": potencia_w,
        "potencia_cv": potencia_cv,
        "corrente": corrente
    }

def gerar_cabecalho(cliente, tecnico, tensao, tipo_partida, vazao, pressao):
    data = datetime.now().strftime("%d/%m/%Y")
    return f"""
Cliente: {cliente}
Técnico: {tecnico}
Data: {data}
Tipo de Partida: {tipo_partida}
Tensão: {tensao}V
Vazão: {vazao} m³/h
Pressão: {pressao} Pa
"""

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

    cliente = st.text_input("Cliente")
    tecnico = st.text_input("Técnico")
    tensao = st.selectbox("Tensão (V)", [220, 380, 440])
    tipo_partida = st.selectbox("Tipo de Partida", ["Direta", "Soft Starter", "Inversor"])

    vazao = st.number_input("Vazão (m³/h)", value=5000)
    pressao = st.number_input("Pressão (Pa)", value=400)

    if st.button("Calcular"):

        motor_data = calcular_motor(vazao, tensao, pressao)

        st.session_state.update({
            "cliente": cliente,
            "tecnico": tecnico,
            "tipo": tipo_partida,
            "tensao": tensao,
            "vazao": vazao,
            "pressao": pressao,
            "motor": motor_data
        })

# =====================================================
# ABA 2 - RESULTADO
# =====================================================

with aba2:

    if "motor" in st.session_state:

        motor = st.session_state.motor

        st.write("### 🌀 Motor")
        st.write(f"Potência: {motor['potencia_cv']:.2f} CV")
        st.write(f"Corrente: {motor['corrente']:.2f} A")

# =====================================================
# ABA 3 - MULTIFILAR
# =====================================================

with aba3:

    if "motor" in st.session_state:

        texto = gerar_cabecalho(
            st.session_state.cliente,
            st.session_state.tecnico,
            st.session_state.tensao,
            st.session_state.tipo,
            st.session_state.vazao,
            st.session_state.pressao
        )

        texto += "\n--- MOTOR ---\n"
        texto += f"Potência CV: {st.session_state.motor['potencia_cv']:.2f}\n"
        texto += f"Corrente: {st.session_state.motor['corrente']:.2f} A\n"

        st.text_area("Diagrama Multifilar", texto, height=300)

# =====================================================
# ABA 4 - MATERIAIS
# =====================================================

with aba4:

    if "motor" in st.session_state:

        corrente = st.session_state.motor["corrente"]

        st.write("### 📦 Lista de Materiais")
        st.write(f"- Disjuntor Tripolar {round(corrente*1.25)} A")
        st.write("- Cabo 6 mm²")
        st.write("- Contator AC-3")

# =====================================================
# ABA 5 - SIMULADOR COMPLETO
# =====================================================

with aba5:

    st.subheader("🎛️ Simulador Industrial - Inversor + CLP")

    rpm_max = 3600
    setpoint = st.number_input("Pressão Alvo (Pa)", 100, 1000, 500)
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

    col1, col2, col3 = st.columns(3)
    col1.metric("RPM Atual", int(rpm))
    col2.metric("Pressão Total (Pa)", pressao_total)
    col3.metric("Erro", round(erro, 1))

    st.progress(rpm / rpm_max)

    # ================= PRESSOSTATOS =================

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

    motor_ligado = not st.session_state.p2_estado

    st.write(f"- Pressostato 1: {'🟡 Alarme' if st.session_state.p1_estado else '🟢 Normal'}")
    st.write(f"- Pressostato 2: {'🔴 Crítico' if st.session_state.p2_estado else '🟢 Normal'}")

    if not motor_ligado:
        st.session_state.rpm_auto = 0
        rpm = 0
        st.error("🚨 Pressão Crítica! CLP Desligando Motor!")

    # ================= MOTOR ANIMADO =================

    st.markdown("### 🌀 Motor")

    if motor_ligado and rpm > 0:

        velocidade_animacao = max(0.2, 3 - (rpm / rpm_max) * 2.5)

        st.markdown(f"""
        <style>
        .motor {{
            width:120px;
            height:120px;
            border:6px solid #2ecc71;
            border-radius:50%;
            margin:auto;
            position:relative;
            animation: spin {velocidade_animacao}s linear infinite;
        }}

        .motor::after {{
            content:"";
            position:absolute;
            width:6px;
            height:50px;
            background:#2ecc71;
            top:10px;
            left:50%;
            transform:translateX(-50%);
            border-radius:3px;
        }}

        @keyframes spin {{
            100% {{ transform: rotate(360deg); }}
        }}
        </style>

        <div class="motor"></div>
        """, unsafe_allow_html=True)

        st.success("🟢 Motor em Operação")

    else:

        st.markdown("""
        <div style="
            width:120px;
            height:120px;
            border:6px solid #e74c3c;
            border-radius:50%;
            margin:auto;
        "></div>
        """, unsafe_allow_html=True)

        st.error("🔴 Motor Parado")
