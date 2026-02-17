import streamlit as st

st.set_page_config(page_title="Gerador de Diagramas Elétricos", layout="wide")

st.title("🔌 GERADOR DE DIAGRAMAS ELÉTRICOS")

# ==========================
# SIDEBAR - DADOS
# ==========================

st.sidebar.header("📋 Dados do Projeto")

cliente = st.sidebar.text_input("Nome do Cliente")
tecnico = st.sidebar.text_input("Nome do Técnico")
motor = st.sidebar.text_input("Modelo do Motor")
potencia = st.sidebar.number_input("Potência (CV)", min_value=0.1, step=0.1)
tensao = st.selectbox("Tensão do Sistema", ["220V", "380V", "440V"])
corrente = st.number_input("Corrente Nominal (A)", min_value=0.1, step=0.1)

st.sidebar.markdown("---")
st.sidebar.header("⚙ Componentes")

modelo_disjuntor = st.sidebar.text_input("Modelo do Disjuntor")
modelo_contator = st.sidebar.text_input("Modelo do Contator")
modelo_rele = st.sidebar.text_input("Modelo do Relé Térmico")

# ==========================
# INFORMAÇÕES
# ==========================

st.subheader("📄 Informações do Projeto")

st.write(f"**Cliente:** {cliente}")
st.write(f"**Técnico:** {tecnico}")
st.write(f"**Motor:** {motor}")
st.write(f"**Potência:** {potencia} CV")
st.write(f"**Tensão:** {tensao}")
st.write(f"**Corrente:** {corrente} A")

# ==========================
# MULTIFILAR MELHORADO
# ==========================

st.subheader("📐 Diagrama Multifilar")

multifilar = f"""
ALIMENTAÇÃO TRIFÁSICA

L1 ───────────────┐
                  │
L2 ───────────────┼──────────────┐
                  │              │
L3 ───────────────┼──────────────┼──────────────┐
                  │              │              │
               (1)            (3)            (5)
            DISJUNTOR {modelo_disjuntor}
               (2)            (4)            (6)
                  │              │              │
                  │              │              │
               (1)            (3)            (5)
            CONTATOR {modelo_contator}
               (2)            (4)            (6)
                  │              │              │
                  │              │              │
                  U              V              W
                    MOTOR {motor}
               {potencia} CV - {tensao}
"""

st.code(multifilar)

# ==========================
# LISTA DE MATERIAIS DINÂMICA
# ==========================

st.subheader("🧾 Lista de Materiais")

st.markdown(f"""
- 1x Disjuntor Tripolar - {modelo_disjuntor}
- 1x Contator Tripolar - {modelo_contator}
- 1x Relé Térmico - {modelo_rele}
- Cabos compatíveis com {corrente} A
- Bornes de passagem
- Trilho DIN
- Canaletas
""")

# ==========================
# SUGESTÃO DE INVERSORES
# ==========================

st.subheader("⚡ Sugestão de Inversores")

st.markdown("""
- WEG CFW300  
- WEG CFW500  
- Schneider Altivar 12  
- Schneider Altivar 320  
""")

# ==========================
# SUGESTÃO DE CLP
# ==========================

st.subheader("🖥 Sugestão de CLP")

st.markdown("""
- WEG CLIC02  
- Siemens LOGO!  
- Schneider Zelio  
- Delta DVP  
""")

st.markdown("---")
st.write("Sistema para apoio técnico e geração de diagrama multifilar.")
