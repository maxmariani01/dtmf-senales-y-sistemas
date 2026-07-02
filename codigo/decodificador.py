"""
decodificador.py
----------------
Lee marcacion.wav, separa los tonos, aplica el banco de 8 correladores y
recupera el numero marcado. Verifica cada resultado contra el metodo FFT.

Ejecutar:  python decodificador.py
Requiere:  haber corrido antes  generador.py  (necesita marcacion.wav)
"""

import numpy as np
from scipy.io import wavfile

from dtmf_comun import FS, F_BAJAS, F_ALTAS, TECLADO, correlacion_cuadratura


def segmentar(x, ventana=0.02, umbral=0.10):
    """
    Detecta donde empieza y termina cada tono midiendo la energia de corto
    plazo en ventanas de 20 ms (idea de senal de potencia local).
    Devuelve una lista de pares (inicio, fin) en muestras.
    """
    L = int(FS * ventana)
    nb = len(x) // L
    e = np.array([np.sum(x[i*L:(i+1)*L]**2) for i in range(nb)])
    activo = e > umbral * e.max()
    segmentos, ini = [], None
    for i, a in enumerate(activo):
        if a and ini is None:
            ini = i
        if not a and ini is not None:
            segmentos.append((ini*L, i*L))
            ini = None
    if ini is not None:
        segmentos.append((ini*L, nb*L))
    return segmentos


def decodificar_segmento(x):
    """Aplica los 8 correladores y decide por doble argmax."""
    Eb = [correlacion_cuadratura(x, f) for f in F_BAJAS]
    Ea = [correlacion_cuadratura(x, f) for f in F_ALTAS]
    i, j = int(np.argmax(Eb)), int(np.argmax(Ea))
    return TECLADO[i][j], Eb, Ea


def decodificar_segmento_fft(x):
    """
    Metodo alternativo: energia |X(k)|^2 del bin mas cercano a cada f.
    Deberia coincidir con el correlador (salvo fuga espectral).
    """
    X = np.abs(np.fft.rfft(x))**2
    f = np.fft.rfftfreq(len(x), 1 / FS)
    energia = lambda f0: X[np.argmin(np.abs(f - f0))]
    i = int(np.argmax([energia(fb) for fb in F_BAJAS]))
    j = int(np.argmax([energia(fa) for fa in F_ALTAS]))
    return TECLADO[i][j]


if __name__ == "__main__":
    fs, wav = wavfile.read("marcacion.wav")
    x = wav.astype(float) / 32767

    resultado = ""
    for (a, b) in segmentar(x):
        tecla, Eb, Ea = decodificar_segmento(x[a:b])
        tecla_fft = decodificar_segmento_fft(x[a:b])
        resultado += tecla
        print(f"[{a/fs:5.2f}-{b/fs:5.2f} s]  correlacion: {tecla}   "
              f"FFT: {tecla_fft}   E_bajas={np.round(Eb, 1)}")

    print("\nNumero decodificado:", resultado)
