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

 elif aba == "🎛️ Simulador":

    st.markdown("### 🎛️ Simulador Industrial - Inversor + CLP")

    pressao_alvo = st.number_input("Pressão Alvo (Pa)", value=500.0)

    sujidade = st.slider("Sujidade do Filtro (%)", 0, 100, 20)

    # --- Cálculo da pressão simulada ---
    pressao_total = 600 - (sujidade * 4)
    erro = pressao_alvo - pressao_total

    # --- Controle simples estilo CLP ---
    rpm = max(0, min(1800, int(erro * 3 + 900)))

    motor_ligado = True
    if pressao_total < 150:
        motor_ligado = False

    st.write("RPM Atual:", rpm)
    st.write("Pressão Total (Pa):", round(pressao_total,1))
    st.write("Erro:", round(erro,1))

    st.markdown("### 🌀 Motor")

    # --- VELOCIDADE DA ANIMAÇÃO BASEADA NO RPM ---
    if motor_ligado and rpm > 0:

        # Quanto maior RPM, mais rápido gira
        velocidade = max(0.2, 2 - (rpm / 1200))

        st.markdown(f"""
        <style>
        .motor-container {{
            display:flex;
            justify-content:center;
            align-items:center;
            margin-top:20px;
        }}

        .motor {{
            width:140px;
            height:140px;
            border:8px solid #2ecc71;
            border-radius:50%;
            position:relative;
            animation: spin {velocidade}s linear infinite;
        }}

        .motor::after {{
            content:"";
            position:absolute;
            width:8px;
            height:60px;
            background:#2ecc71;
            top:15px;
            left:50%;
            transform:translateX(-50%);
            border-radius:4px;
        }}

        @keyframes spin {{
            100% {{ transform: rotate(360deg); }}
        }}
        </style>

        <div class="motor-container">
            <div class="motor"></div>
        </div>
        """, unsafe_allow_html=True)

        st.success("🟢 Motor em Operação")

    else:

        st.markdown("""
        <style>
        .motor-off {
            width:140px;
            height:140px;
            border:8px solid #e74c3c;
            border-radius:50%;
            margin:auto;
            margin-top:20px;
        }
        </style>

        <div class="motor-off"></div>
        """, unsafe_allow_html=True)

        st.error("🔴 Motor Desligado")
    
        
