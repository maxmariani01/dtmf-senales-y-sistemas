"""
analisis_validacion.py
----------------------
Genera evidencias adicionales para el informe:

  Figura 1 (correladores.png) : banco de 8 correladores E(f) para un tono.
                                Visualiza el mecanismo de deteccion: de las 8
                                frecuencias, solo se "encienden" 2.
  Figura 2 (espectro_tono.png): espectro |X(f)| de un tono con los 2 picos
                                marcados. Conecta con la DFT del TP6.
  Figura 3 (espectrograma.png): mapa tiempo-frecuencia de una secuencia.
                                Cada tecla aparece como un par de bandas.
  Consola                     : contraste prediccion analitica vs medicion.

Ejecutar:  python analisis_validacion.py
"""

import numpy as np
import matplotlib.pyplot as plt

from dtmf_comun import FS, A, F_BAJAS, F_ALTAS, DTMF, correlacion_cuadratura
from generador import tono, secuencia


# =====================================================================
# Figura 1 - Banco de correladores para una tecla
# =====================================================================
tecla = "5"
x = tono(tecla)
fL, fH = DTMF[tecla]
frecs = F_BAJAS + F_ALTAS
E = np.array([correlacion_cuadratura(x, f) for f in frecs])
etiquetas = [str(f) for f in frecs]
colores = ["#1f77b4" if f in (fL, fH) else "#cccccc" for f in frecs]

fig, (axL, axR) = plt.subplots(1, 2, figsize=(12, 5))
axL.bar(etiquetas, E, color=colores)
axL.set(title="Escala lineal: la selectividad",
        xlabel="Frecuencia patron [Hz]", ylabel="E(f) = C^2 + S^2")
axL.tick_params(axis="x", rotation=45)

axR.bar(etiquetas, E, color=colores)
axR.set_yscale("log")
axR.set(title="Escala log: la brecha (4-5 ordenes)",
        xlabel="Frecuencia patron [Hz]", ylabel="E(f)  [log]")
axR.tick_params(axis="x", rotation=45)

fig.suptitle(f'Banco de 8 correladores - tecla "{tecla}"  (fL={fL} Hz, fH={fH} Hz)')
plt.tight_layout()
plt.savefig("correladores.png", dpi=150)
print("Guardada: correladores.png")


# =====================================================================
# Figura 2 - Espectro de un tono con los picos marcados
# =====================================================================
X = np.abs(np.fft.rfft(x))
f = np.fft.rfftfreq(len(x), 1 / FS)

plt.figure(figsize=(9, 5))
plt.plot(f, X, lw=1)
plt.xlim(0, 2000)
for fp, nombre in [(fL, "fL"), (fH, "fH")]:
    k = np.argmin(np.abs(f - fp))
    plt.annotate(f"{nombre} = {fp} Hz", xy=(f[k], X[k]),
                 xytext=(f[k] + 90, X[k] * 0.9),
                 arrowprops=dict(arrowstyle="->"))
plt.title(f'Espectro |X(f)| del tono "{tecla}"  (DFT)')
plt.xlabel("f [Hz]")
plt.ylabel("|X(f)|")
plt.tight_layout()
plt.savefig("espectro_tono.png", dpi=150)
print("Guardada: espectro_tono.png")


# =====================================================================
# Figura 3 - Espectrograma de una secuencia (tiempo-frecuencia)
# =====================================================================
numero = "1234567890"          # 10 digitos: usa las 8 frecuencias
xs = secuencia(numero)

plt.figure(figsize=(11, 5))
plt.specgram(xs, NFFT=1024, Fs=FS, noverlap=512, cmap="inferno")
plt.ylim(0, 2000)
plt.title(f'Espectrograma de la secuencia "{numero}"')
plt.xlabel("Tiempo [s]")
plt.ylabel("Frecuencia [Hz]")
plt.colorbar(label="Intensidad [dB]")
plt.tight_layout()
plt.savefig("espectrograma.png", dpi=150)
print("Guardada: espectrograma.png")


# =====================================================================
# Consola - Contraste prediccion analitica vs medicion
# =====================================================================
N = len(x)
pred = (A * N / 2) ** 2
medido = correlacion_cuadratura(x, fL)
error = abs(medido - pred) / pred * 100

print("\n===== Contraste prediccion analitica vs medicion (tecla '5') =====")
print(f"N (muestras por tono)        : {N}")
print(f"Prediccion E = (A*N/2)^2     : {pred:,.0f}")
print(f"Medicion E({fL} Hz)           : {medido:,.0f}")
print(f"Error relativo               : {error:.3f} %")
print(f"Maxima energia ausente       : {E[E < pred/100].max():,.0f}")
print(f"  -> {pred / E[E < pred/100].max():,.0f} veces menor que el pico")
