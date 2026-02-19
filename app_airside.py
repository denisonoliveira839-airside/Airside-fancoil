import streamlit as st
import math

st.set_page_config(page_title="AirSide PRO", layout="wide")

# ===============================
# CSS GLOBAL (Motor + Estilo)
# ===============================

st.markdown("""
<style>
.motor-container {
    display:flex;
    justify-content:center;
    align-items:center;
    margin-top:20px;
}

.motor {
    width:140px;
    height:140px;
    border:8px solid #2ecc71;
    border-radius:50%;
    position:relative;
}

.motor::after {
    content:"";
    position:absolute;
    width:8px;
    height:60px;
    background:#2ecc71;
    top:15px;
    left:50%;
    transform:translateX(-50%);
    border-radius:4px;
}

.motor-off {
    width:140px;
    height:140px;
    border:8px solid #e74c3c;
    border-radius:50%;
    margin:auto;
    margin-top:20px;
}

@keyframes spin {
    100% { transform: rotate(360deg); }
}
</style>
""", unsafe_allow_html=True)

# ===============================
# MENU LATERAL
# ===============================

st.sidebar.title("🌀 AirSide PRO")
aba = st.sidebar.radio(
    "Navegação",
    ["📋 Dados", "📊 Resultado", "📑 Multifilar", "📦 Materiais", "🎛️ Simulador"]
)

# ===============================
# ABA 1 - DADOS
# ===============================

if aba == "📋 Dados":

    st.title("📋 Dados do Sistema")

    vazao = st.number_input("Vazão (m³/h)", value=5000.0)
    pressao = st.number_input("Pressão (Pa)", value=500.0)
    rendimento = st.slider("Rendimento (%)", 50, 100, 85)

    st.session_state["vazao"] = vazao
    st.session_state["pressao"] = pressao
    st.session_state["rendimento"] = rendimento


# ===============================
# ABA 2 - RESULTADO
# ===============================

elif aba == "📊 Resultado":

    st.title("📊 Resultado")

    vazao = st.session_state.get("vazao", 5000)
    pressao = st.session_state.get("pressao", 500)
    rendimento = st.session_state.get("rendimento", 85)

    potencia = (vazao * pressao) / (367 * rendimento)

    st.metric("Potência Estimada (kW)", round(potencia, 2))


# ===============================
# ABA 3 - MULTIFILAR
# ===============================

elif aba == "📑 Multifilar":

    st.title("📑 Diagrama Multifilar")

    st.write("Motor Trifásico 380V")
    st.write("Disjuntor Motor")
    st.write("Contator")
    st.write("Relé Térmico")
    st.write("Inversor de Frequência")


# ===============================
# ABA 4 - MATERIAIS
# ===============================

elif aba == "📦 Materiais":

    st.title("📦 Lista de Materiais")

    materiais = [
        "Motor Trifásico",
        "Inversor de Frequência",
        "Disjuntor Motor",
        "Contator",
        "Relé Térmico",
        "Pressostato 1",
        "Pressostato 2",
        "CLP Industrial"
    ]

    for item in materiais:
        st.write("•", item)


# ===============================
# ABA 5 - SIMULADOR
# ===============================

elif aba == "🎛️ Simulador":

    st.title("🎛️ Simulador Industrial - Inversor + CLP")

    pressao_alvo = st.number_input("Pressão Alvo (Pa)", value=500.0)
    sujidade = st.slider("Sujidade do Filtro (%)", 0, 100, 20)

    # Simulação de pressão
    pressao_total = 700 - (sujidade * 5)
    erro = pressao_alvo - pressao_total

    # Controle tipo CLP
    rpm = max(0, min(1800, int(erro * 3 + 900)))

    # Pressostatos
    p1_ativar = 450
    p1_desativar = 500
    p2_critico = 650
    p2_reset = 600

    st.write("RPM Atual:", rpm)
    st.write("Pressão Total (Pa):", round(pressao_total, 1))
    st.write("Erro:", round(erro, 1))

    st.subheader("Pressostatos")

    if pressao_total >= p2_critico:
        st.error("🔴 Pressostato 2: CRÍTICO")
        st.error("🚨 Pressão Crítica! CLP Desligando Motor!")
        motor_ligado = False

    elif pressao_total >= p1_ativar:
        st.warning("🟡 Pressostato 1: Alarme")
        motor_ligado = True

    else:
        st.success("🟢 Pressão Normal")
        motor_ligado = True

    # ===============================
    # MOTOR COM ANIMAÇÃO
    # ===============================

    st.markdown("### 🌀 Motor")

    if motor_ligado and rpm > 0:

        velocidade = max(0.2, 2 - (rpm / 1200))

        st.markdown(f"""
        <div class="motor-container">
            <div class="motor" style="animation: spin {velocidade}s linear infinite;"></div>
        </div>
        """, unsafe_allow_html=True)

        st.success("🟢 Motor em Operação")

    else:

        st.markdown("""
        <div class="motor-container">
            <div class="motor-off"></div>
        </div>
        """, unsafe_allow_html=True)

        st.error("🔴 Motor Desligado")
