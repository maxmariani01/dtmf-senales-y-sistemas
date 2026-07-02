"""
captura_microfono.py
--------------------
Prueba el decodificador DTMF con tonos REALES capturados por microfono
(o leidos de un .wav grabado con el celular / Audacity).

Maneja el detalle clave: el microfono graba a 44100/48000 Hz y el proyecto
trabaja a 8000 Hz, asi que resamplea antes de decodificar.

--- Dependencia extra (solo para MODO = "grabar") ---
    pip install sounddevice
    (o)  conda install -c conda-forge python-sounddevice

--- Como usarlo ---
    1) Elegir MODO:
         "grabar"  -> graba del microfono DURACION segundos
         "archivo" -> decodifica un .wav ya grabado (no precisa sounddevice)
    2) Poner ETIQUETA en "limpio" o "ruido" segun la prueba.
    3) Reproducir los tonos DTMF cerca del microfono (app de telefono,
       el marcacion.wav por el parlante, o un generador DTMF online).
    4) python captura_microfono.py
"""

import numpy as np
from math import gcd
from pathlib import Path
from scipy.io import wavfile
from scipy.signal import resample_poly

from dtmf_comun import FS                       # 8000 Hz (objetivo)
from decodificador import segmentar, decodificar_segmento

BASE_DIR = Path(__file__).resolve().parent

# ===================== CONFIGURACION =====================
MODO     = "grabar"      # "grabar"  o  "archivo"
ETIQUETA = "ruido"      # "limpio"  o  "ruido"  (solo para nombrar la evidencia)
DURACION = 6             # segundos a grabar (modo "grabar")
FS_MIC   = 44100         # frecuencia del microfono (modo "grabar")
ARCHIVO  = BASE_DIR / "grabacion.wav"   # .wav a leer (modo "archivo")
UMBRAL   = 0.20          # sensibilidad del segmentador (subir si hay ruido)
# ========================================================


def grabar(seg, fs_mic):
    """Graba seg segundos del microfono. Importa sounddevice aca adentro
    para que el modo 'archivo' no lo necesite."""
    import sounddevice as sd
    print(f"Grabando {seg} s a {fs_mic} Hz... reproduci los tonos AHORA.")
    audio = sd.rec(int(seg * fs_mic), samplerate=fs_mic, channels=1, dtype="float64")
    sd.wait()
    print("Grabacion terminada.")
    return audio[:, 0]


def leer_wav(path):
    """Lee un .wav de cualquier frecuencia, lo pasa a mono y float."""
    fs_mic, data = wavfile.read(path)
    data = data.astype(np.float64)
    if data.ndim == 2:                 # estereo -> promedio de canales
        data = data.mean(axis=1)
    if np.max(np.abs(data)) > 1.0:     # si venia en enteros, normalizar
        data /= np.max(np.abs(data))
    return data, fs_mic


def a_8000(x, fs_mic):
    """Resamplea de fs_mic a 8000 Hz (incluye filtro anti-aliasing)."""
    if fs_mic == FS:
        return x
    g = gcd(int(fs_mic), FS)
    return resample_poly(x, FS // g, int(fs_mic) // g)


def estimar_snr(x, segmentos):
    """SNR aproximada: potencia en los tramos con tono vs los silencios."""
    if not segmentos:
        return None
    mascara = np.ones(len(x), bool)
    activo = []
    for (a, b) in segmentos:
        activo.append(x[a:b])
        mascara[a:b] = False
    p_sig = np.mean(np.concatenate(activo) ** 2)
    p_noi = np.mean(x[mascara] ** 2) + 1e-12
    return 10 * np.log10(p_sig / p_noi)


if __name__ == "__main__":
    # 1) obtener el audio crudo + su frecuencia
    if MODO == "grabar":
        crudo, fs_origen = grabar(DURACION, FS_MIC), FS_MIC
    else:
        crudo, fs_origen = leer_wav(ARCHIVO)
        print(f"Archivo leido: {ARCHIVO}  ({fs_origen} Hz, {len(crudo)/fs_origen:.2f} s)")

    # 2) llevar a 8000 Hz y normalizar
    x = a_8000(crudo, fs_origen)
    x = x / (np.max(np.abs(x)) + 1e-9)

    # 3) guardar evidencia ya resampleada
    nombre = BASE_DIR / f"captura_{ETIQUETA}.wav"
    wavfile.write(nombre, FS, (x * 32767).astype(np.int16))
    print("Evidencia guardada:", nombre)

    # 4) segmentar, estimar SNR y decodificar
    segs = segmentar(x, umbral=UMBRAL)
    snr = estimar_snr(x, segs)
    if snr is not None:
        print(f"SNR estimada: {snr:.1f} dB   (tramos con tono: {len(segs)})")

    resultado = "".join(decodificar_segmento(x[a:b])[0] for (a, b) in segs)
    print(f"\n[{ETIQUETA}] Numero decodificado:  {resultado or '(nada detectado)'}")
