"""
espectrogramas_captura.py
-------------------------
Genera los espectrogramas comparativos de las capturas reales de microfono:
captura_limpio.wav  vs  captura_ruido.wav, lado a lado.

Requiere haber corrido antes captura_microfono.py en ambos modos
(ETIQUETA = "limpio" y ETIQUETA = "ruido").

Ejecutar:  python espectrogramas_captura.py
Genera:    espectrogramas_captura.png
"""

from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile

from dtmf_comun import FS

BASE_DIR = Path(__file__).resolve().parent

ARCHIVOS = [(BASE_DIR / "captura_limpio.wav", "Captura limpia"),
            (BASE_DIR / "captura_ruido.wav",  "Captura con ruido")]

# Filtra los que existan, para que no falle si todavia no se grabó nada
presentes = [(f, t) for (f, t) in ARCHIVOS if f.exists()]
if not presentes:
    raise SystemExit("No encontre captura_limpio.wav ni captura_ruido.wav. "
                     "Corre primero captura_microfono.py en cada modo.")

fig, axes = plt.subplots(1, len(presentes), figsize=(6 * len(presentes), 5),
                         squeeze=False)

for ax, (archivo, titulo) in zip(axes[0], presentes):
    fs, data = wavfile.read(archivo)
    x = data.astype(float)
    if x.ndim == 2:                 # por si quedo estereo
        x = x.mean(axis=1)
    x /= (np.max(np.abs(x)) + 1e-9)

    ax.specgram(x, NFFT=1024, Fs=fs, noverlap=512, cmap="inferno")
    ax.set_ylim(0, 2000)
    ax.set_title(titulo)
    ax.set_xlabel("Tiempo [s]")
    ax.set_ylabel("Frecuencia [Hz]")

    # marcar las 8 frecuencias DTMF como referencia
    for f0 in [697, 770, 852, 941, 1209, 1336, 1477, 1633]:
        ax.axhline(f0, color="cyan", lw=0.3, alpha=0.4)

plt.tight_layout()
salida = BASE_DIR / "espectrogramas_captura.png"
plt.savefig(salida, dpi=150)
print(f"Guardada: {salida}")
plt.show()
