import streamlit as st
import math

st.set_page_config(page_title="AirSide - Ventilação Industrial", layout="centered")

st.title("🌀 AirSide - Dimensionamento Elétrico de Ventiladores")

# =========================
# DIAGRAMA UNIFILAR
# =========================
def gerar_diagrama_unifilar(tensao, disj_geral, disj_motor, motor):
    return f"""
REDE {tensao}V
   │
   ├── Disjuntor Geral {disj_geral}A
   │
   ├── Inversor de Frequência
   │
   ├── Disjuntor Motor {disj_motor}A
   │
   └── Motor {motor} CV
"""

# =========================
# DIAGRAMA MULTIFILAR
# =========================
def gerar_diagrama_multifilar(tensao, motor, corrente):

    return f"""
ALIMENTAÇÃO {tensao}V

L1 ── Disj Geral ── Inversor ── Disj Motor ──┐
L2 ── Disj Geral ── Inversor ── Disj Motor ──┼── Motor {motor}CV
L3 ── Disj Geral ── Inversor ── Disj Motor ──┘

COMANDO:

Fonte 24Vcc
   │
   ├── CLP
   │     ├── Entrada Pressostato 1
   │     ├── Entrada Pressostato 2
   │     └── Saída RUN Inversor
"""

# =========================
# CÁLCULO MOTOR (BLINDADO)
# =========================
def calcular_motor(vazao, tensao, pressao_total=500, rendimento=0.65):

    try:
        vazao = float(vazao)
        pressao_total = float(pressao_total)
        rendimento = float(rendimento)
        tensao_int = int(tensao)

        if vazao <= 0:
            vazao = 100

        if pressao_total <= 0:
            pressao_total = 500

        if rendimento <= 0:
            rendimento = 0.65

        potencia_kw = (vazao * pressao_total) / (rendimento * 3600000)
        potencia_kw *= 1.15

        potencia_cv = potencia_kw / 0.736
        potencia_motor = max(1, math.ceil(potencia_cv))

        corrente = round(
            (potencia_kw * 1000) / (math.sqrt(3) * tensao_int * 0.85),
            2
        )

        disj_motor = max(2, math.ceil(corrente * 1.25))
        disj_geral = max(6, math.ceil(disj_motor * 1.2))

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

        return potencia_motor, corrente, disj_motor, disj_geral, cabo_motor

    except Exception as e:
        print("Erro no calcular_motor:", e)
        return 1, 0, 10, 16, 2.5


# =========================
# ENTRADAS
# =========================
vazao = st.number_input("Vazão (m³/h)", min_value=100.0, value=5000.0)
tensao = st.selectbox("Tensão (V)", [220, 380, 440])
pressao = st.number_input("Pressão Total (Pa)", min_value=100.0, value=500.0)

# =========================
# BOTÃO CALCULAR
# =========================
if st.button("🔎 Calcular Sistema"):

    motor, corrente, disj_motor, disj_geral, cabo_motor = calcular_motor(
        vazao, tensao, pressao
    )

    st.success("Dimensionamento concluído!")

    st.markdown("## 🔧 Resultado Técnico")

    st.write(f"**Motor:** {motor} CV")
    st.write(f"**Corrente estimada:** {corrente} A")
    st.write(f"**Disjuntor Motor:** {disj_motor} A")
    st.write(f"**Disjuntor Geral:** {disj_geral} A")
    st.write(f"**Cabo Motor recomendado:** {cabo_motor} mm²")
    st.write("**Sistema de partida:** Inversor de Frequência")
    st.write("**Automação:** CLP + 2 Pressostatos")

    st.markdown("## 📊 Diagrama Unifilar")
    st.code(gerar_diagrama_unifilar(tensao, disj_geral, disj_motor, motor))

    st.markdown("## 📊 Diagrama Multifilar")
    st.code(gerar_diagrama_multifilar(tensao, motor, corrente))
