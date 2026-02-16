# gerador_pdf.py
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def gerar_pdf(vazao, tensao, motor, partida, corrente, disj_motor, cabo_motor,
              pot_banco, corrente_banco, disj_banco):
    arquivo = "Projeto_Executivo_Fancoil_FINAL.pdf"
    c = canvas.Canvas(arquivo, pagesize=A4)
    c.setFont("Helvetica", 12)
    c.drawString(50, 800, "PROJETO EXECUTIVO FANCOIL")
    c.drawString(50, 780, f"Vazão: {vazao} m³/h")
    c.drawString(50, 760, f"Tensão: {tensao} V")
    c.drawString(50, 740, f"Motor: {motor} CV")
    c.drawString(50, 720, f"Partida: {partida}")
    c.drawString(50, 700, f"Corrente nominal: {corrente} A")
    c.drawString(50, 680, f"Disjuntor Motor: {disj_motor} A")
    c.drawString(50, 660, f"Cabo Motor: {cabo_motor} mm²")
    if pot_banco > 0:
        c.drawString(50, 640, f"Banco de resistência: {pot_banco} kW")
        c.drawString(50, 620, f"Corrente Banco: {corrente_banco} A")
        c.drawString(50, 600, f"Disjuntor Banco: {disj_banco} A")
    c.save()
