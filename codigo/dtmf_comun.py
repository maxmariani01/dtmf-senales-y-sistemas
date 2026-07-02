"""
dtmf_comun.py
-------------
Modulo compartido del proyecto DTMF: tabla de frecuencias, constantes
del sistema y la funcion de correlacion en cuadratura.

Este archivo NO se ejecuta solo: lo importan los demas scripts.
"""

import numpy as np

# ---- Constantes del sistema -------------------------------------------------
FS    = 8000      # frecuencia de muestreo [Hz] (estandar telefonico)
T_ON  = 0.40      # duracion de cada tono [s]
T_OFF = 0.10      # silencio entre tonos [s]
A     = 0.5       # amplitud de cada senoidal

# ---- Tabla DTMF 4x4 ---------------------------------------------------------
F_BAJAS = [697, 770, 852, 941]       # grupo bajo  (filas)
F_ALTAS = [1209, 1336, 1477, 1633]   # grupo alto  (columnas)
TECLADO = [['1', '2', '3', 'A'],
           ['4', '5', '6', 'B'],
           ['7', '8', '9', 'C'],
           ['*', '0', '#', 'D']]

# Diccionario  tecla -> (fL, fH)  construido desde la matriz
DTMF = {TECLADO[i][j]: (F_BAJAS[i], F_ALTAS[j])
        for i in range(4) for j in range(4)}


def correlacion_cuadratura(x, f, fs=FS):
    """
    Energia E(f) = C(f)^2 + S(f)^2 del segmento x en la frecuencia f.

    C y S son las correlaciones de la senal contra los patrones coseno y
    seno respectivamente. La suma de cuadrados hace que el resultado sea
    independiente de la fase del tono (ver desarrollo teorico).
    """
    m = np.arange(len(x))
    C = np.sum(x * np.cos(2 * np.pi * f * m / fs))
    S = np.sum(x * np.sin(2 * np.pi * f * m / fs))
    return C**2 + S**2
