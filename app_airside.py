import streamlit as st
import time
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

st.title("🔧 Sistema de Dimensionamento + Simuladores")

# =====================================================
# CRIAÇÃO DAS ABAS PRINCIPAIS
# =====================================================
abas = st.tabs([
    "📊 Dados",
    "📈 Resultados",
    "📐 Multifilar",
    "📦 Materiais",
    "🧮 Resistência",
    "🎛️ Simulador Inversor + CLP"
])

# =====================================================
# ABA 1 - DADOS
# =====================================================
with abas[0]:
    st.header("Dados do Projeto")
    st.write("Conteúdo original permanece aqui...")

# =====================================================
# ABA 2 - RESULTADOS
# =====================================================
with abas[1]:
    st.header("Resultados")
    st.write("Conteúdo original permanece aqui...")

# =====================================================
# ABA 3 - MULTIFILAR
# =====================================================
with abas[2]:
    st.header("Diagrama Multifilar")
    st.write("Conteúdo original permanece aqui...")

# =====================================================
# ABA 4 - MATERIAIS
# =====================================================
with abas[3]:
    st.header("Lista de Materiais")
    st.write("Conteúdo original permanece aqui...")

# =====================================================
# ABA 5 - RESISTÊNCIA
# =====================================================
with abas[4]:
    st.header("Cálculo de Resistência")
    st.write("Conteúdo original permanece aqui...")

# =====================================================
# ABA 6 - SIMULADOR INVERSOR + CLP
# =====================================================
with abas[5]:

    st.header("💨 Simulação: Inversor + CLP + Pressostatos")

    # -------------------------
    # CONFIGURAÇÕES INVERSOR
    # -------------------------
    velocidade_max = st.number_input("Velocidade Máxima do Ventilador (%)", 10, 100, 100)
    incremento = st.number_input("Incremento de Velocidade por Passo (%)", 1, 10, 2)
    intervalo = st.number_input("Intervalo entre passos (s)", 0.1, 2.0, 0.2, 0.1)

    # -------------------------
    # CONFIGURAÇÕES PRESSOSTATOS
    # -------------------------
    p1_ativar = st.number_input("Pressostato 1 - Ativar em (%)", 0, 100, 60)
    p2_ativar = st.number_input("Pressostato 2 - Ativar em (%)", 0, 100, 80)

    nivel_inicial = st.slider("Nível inicial de sujeira do filtro (%)", 0, 100, 0)

    iniciar = st.button("▶ Iniciar Simulação")

    if iniciar:

        ventilador_ligado = True
        velocidade = 0
        nivel = nivel_inicial

        velocidades = []
        niveis = []
        press1_status = []
        press2_status = []
        log = []

        while ventilador_ligado and velocidade < velocidade_max:

            velocidade += incremento

            press1 = nivel >= p1_ativar
            press2 = nivel >= p2_ativar

            if press1 or press2:
                ventilador_ligado = False
                log.append(f"⚠ Pressostato ativado! Inversor desligado em {velocidade}%")
                break
            else:
                log.append(f"Ventilador rodando em {velocidade}%")

            velocidades.append(velocidade)
            niveis.append(nivel)
            press1_status.append(int(press1))
            press2_status.append(int(press2))

            nivel += 1
            if nivel > 100:
                nivel = 100

            time.sleep(intervalo)

        # STATUS FINAL
        st.subheader("📋 Log da Simulação")
        st.text("\n".join(log))

        st.markdown(f"**Ventilador:** {'🟢 Ligado' if ventilador_ligado else '🔴 Desligado'}")
        st.markdown(f"**Pressostato 1:** {'🟢 Ativado' if press1 else '🔴 Desligado'}")
        st.markdown(f"**Pressostato 2:** {'🟢 Ativado' if press2 else '🔴 Desligado'}")

        # -------------------------
        # GRÁFICO
        # -------------------------
        fig, ax1 = plt.subplots()

        ax1.plot(velocidades, marker='o')
        ax1.set_ylabel("Velocidade (%)")
        ax1.set_xlabel("Passos")

        ax2 = ax1.twinx()
        ax2.plot(niveis, linestyle='--')
        ax2.set_ylabel("Nível do Filtro (%)")

        st.pyplot(fig)
