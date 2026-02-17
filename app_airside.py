import streamlit as st

st.set_page_config(page_title="Gerador de Diagramas Elétricos", layout="wide")

st.title("🔌 GERADOR DE DIAGRAMA MULTIFILAR")

# =============================
# DADOS DO PROJETO
# =============================

st.sidebar.header("📋 Dados do Projeto")

cliente = st.sidebar.text_input("Nome do Cliente")
tecnico = st.sidebar.text_input("Nome do Técnico")
potencia = st.sidebar.number_input("Potência do Motor (CV)", min_value=1.0, step=0.5)
tensao = st.sidebar.selectbox("Tensão", ["220V", "380V", "440V"])

st.subheader("📄 Informações")

st.write(f"**Cliente:** {cliente}")
st.write(f"**Técnico:** {tecnico}")
st.write(f"**Motor:** {potencia} CV - {tensao}")

# =============================
# MULTIFILAR
# =============================

st.subheader("📐 Diagrama Multifilar")

multifilar = f"""
ALIMENTAÇÃO TRIFÁSICA

L1  ───────────────┐
                   │
L2  ───────────────┼──────────────┐
                   │              │
L3  ───────────────┼──────────────┼──────────────┐
                   │              │              │
                (1)            (3)            (5)
              DISJUNTOR TRIFÁSICO
                (2)            (4)            (6)
                   │              │              │
                   │              │              │
                (1)            (3)            (5)
                CONTATOR K1
                (2)            (4)            (6)
                   │              │              │
                   │              │              │
                   U              V              W
                        MOTOR TRIFÁSICO
                      {potencia} CV - {tensao}
"""

st.code(multifilar)

# =============================
# LISTA DE MATERIAIS
# =============================

st.subheader("🧾 Lista de Materiais Sugerida")

st.markdown("""
### ⚡ Proteção e Potência
- 1x Disjuntor Tripolar Curva C
- 1x Contator Tripolar (Bobina 220V ou 380V)
- 1x Relé Térmico compatível

### ⚙ Sugestão de Inversores
- WEG CFW300
- WEG CFW500
- Schneider Altivar 12
- Schneider Altivar 320

### 🖥 Sugestão de CLPs
- WEG CLIC02
- Siemens LOGO!
- Schneider Zelio
- Delta DVP

### 🔩 Outros Materiais
- Bornes de passagem
- Trilho DIN
- Canaletas
- Cabo PP ou Cabo 750V
- Terminais tipo olhal
""")

# =============================
# RODAPÉ
# =============================

st.markdown("---")
st.write("Sistema gerado automaticamente para apoio técnico.")
