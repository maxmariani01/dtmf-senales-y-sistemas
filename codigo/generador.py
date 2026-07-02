"""
generador.py
------------
Sintetiza el audio DTMF de una secuencia de teclas, lo guarda como .wav
y grafica la senal en el tiempo y su espectro.

Ejecutar:  python generador.py
Genera:    marcacion.wav  y  generador.png
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile

from dtmf_comun import FS, T_ON, T_OFF, A, DTMF


def tono(tecla):
    """Senal x_k(m) de una tecla: suma de dos senoidales durante T_ON."""
    fL, fH = DTMF[tecla]
    m = np.arange(int(FS * T_ON))
    return A * np.sin(2 * np.pi * fL * m / FS) + A * np.sin(2 * np.pi * fH * m / FS)


def secuencia(digitos):
    """Concatena tonos y silencios: la x(m) de la marcacion completa."""
    sil = np.zeros(int(FS * T_OFF))
    bloques = [sil]
    for d in digitos:
        bloques += [tono(d), sil]
    return np.concatenate(bloques)


if __name__ == "__main__":
    numero = "555"
    x = secuencia(numero)
    t = np.arange(len(x)) / FS

    # --- guardar el audio (16 bits, normalizado) ---
    wav = (x / np.max(np.abs(x)) * 32767).astype(np.int16)
    wavfile.write("marcacion.wav", FS, wav)
    print(f"Audio guardado: marcacion.wav  ({len(x)} muestras, {len(x)/FS:.2f} s)")

    # --- graficas: panorama, zoom y espectro ---
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 9))

    ax1.plot(t, x, lw=0.4)
    ax1.set(title=f"Secuencia DTMF: {numero}", xlabel="t [s]", ylabel="x(t)")

    # zoom de 20 ms al primer tono, para VER la suma de dos senoidales
    i0 = int(FS * T_OFF)
    i1 = i0 + int(FS * 0.020)
    ax2.plot(t[i0:i1] * 1000, x[i0:i1])
    ax2.set(title="Detalle (20 ms): batido de las dos senoidales",
            xlabel="t [ms]", ylabel="x(t)")

    # espectro de toda la secuencia: un pico por frecuencia usada
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / FS)
    ax3.plot(f, np.abs(X))
    ax3.set(title="Espectro |X(f)|", xlabel="f [Hz]", ylabel="|X(f)|", xlim=(0, 2000))

    plt.tight_layout()
    plt.savefig("generador.png", dpi=150)
    print("Grafica guardada: generador.png")
    plt.show()
