"""
robustez_ruido.py
-----------------
Mide la tasa de acierto del banco de correladores en funcion de la relacion
senal/ruido (SNR). Prueba tonos individuales con ruido blanco gaussiano.

Ejecutar:  python robustez_ruido.py
Genera:    robustez.png
"""

import numpy as np
import matplotlib.pyplot as plt

from dtmf_comun import DTMF
from generador import tono
from decodificador import decodificar_segmento


def agregar_ruido(x, snr_db):
    """
    Suma ruido blanco gaussiano con la SNR pedida.
    SNR_dB = 10*log10(P_senal / P_ruido)  ->  P_ruido = P_senal / 10^(SNR/10)
    """
    p_senal = np.mean(x**2)
    p_ruido = p_senal / 10**(snr_db / 10)
    return x + np.random.normal(0, np.sqrt(p_ruido), len(x))


if __name__ == "__main__":
    teclas = list(DTMF.keys())
    snrs = np.arange(-30, 7, 3)
    aciertos = []

    for snr in snrs:
        ok, ensayos = 0, 200
        for _ in range(ensayos):
            k = np.random.choice(teclas)          # tecla al azar
            y = agregar_ruido(tono(k), snr)       # un tono + ruido
            ok += (decodificar_segmento(y)[0] == k)
        aciertos.append(100 * ok / ensayos)
        print(f"SNR = {snr:+3d} dB  ->  acierto {aciertos[-1]:5.1f} %")

    plt.figure(figsize=(8, 5))
    plt.plot(snrs, aciertos, "o-")
    plt.xlabel("SNR [dB]")
    plt.ylabel("Acierto [%]")
    plt.title("Robustez del banco de correladores frente a ruido")
    plt.grid(True)
    plt.savefig("robustez.png", dpi=150)
    print("Grafica guardada: robustez.png")
    plt.show()
