# gerador_multifilar.py
import schemdraw
import schemdraw.elements as elm
import math

def gerar_multifilar(vazao, tensao, motor, partida, pot_banco):
    d = schemdraw.Drawing()
    d.config(fontsize=12)

    # Linha de comando
    d += elm.Line().right().length(0.5)
    d += elm.RBox(w=1, h=0.5).label(f"Q1\nDisjuntor").fill('lightblue')
    d += elm.Line().right().length(0.5)
    d += elm.RBox(w=1, h=0.5).label(f"K1\nContator").fill('lightgreen')
    d += elm.Line().right().length(0.5)
    d += elm.RBox(w=1, h=0.5).label(f"F1\nRelé térmico").fill('lightcoral')
    d += elm.Line().right().length(0.5)
    d += elm.Motor().right().label('M1\nMotor 3~')

    # Banco de resistência
    if pot_banco > 0:
        qtd_res = math.ceil(pot_banco / 2)  # 2 kW por unidade exemplo
        d += elm.Line().down().length(1)
        d += elm.RBox(w=1, h=0.5).label(f"{qtd_res} x 2 kW Resistência").fill('orange')

    d.draw()
    d.save("Multifilar_Fancoil.png")
