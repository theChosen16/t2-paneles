# -*- coding: utf-8 -*-
"""
Genera output/Extra_Resultados/poa_irradiance_cmp22.png en español.

Lee la columna POA CMP22 (índice 1) de los 11 CSV originales de Cocoa con
lectura streaming (mismo patrón de fase2: 3 líneas de cabecera, sentinelas
-9999, fila de ancho variable) y grafica la mediana diaria suavizada (7 días)
por archivo, coloreada por familia tecnológica, con leyenda de 5 grupos.
"""
import csv
import os
from datetime import datetime

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.lines import Line2D
import pandas as pd

plt.style.use('dark_background')
plt.rcParams['figure.facecolor'] = 'none'
plt.rcParams['axes.facecolor'] = 'none'
plt.rcParams['savefig.facecolor'] = 'none'
plt.rcParams['grid.color'] = '#44445c'
plt.rcParams['grid.alpha'] = 0.4
plt.rcParams['text.color'] = '#FFFFFF'
plt.rcParams['axes.labelcolor'] = '#FFFFFF'
plt.rcParams['xtick.color'] = '#CCCCCC'
plt.rcParams['ytick.color'] = '#CCCCCC'

BASE = 'Base datos original/Cocoa'

GRUPOS = {  # familia -> (color, archivos)
    'm-Si / x-Si': ('#00D2FF', ['Cocoa_mSi0166.csv', 'Cocoa_mSi0188.csv',
                                'Cocoa_mSi460A8.csv', 'Cocoa_xSi12922.csv']),
    'HIT':         ('#F1C40F', ['Cocoa_HIT05667.csv']),
    'CdTe':        ('#2ECC71', ['Cocoa_CdTe75638.csv']),
    'CIGS':        ('#FF5E3A', ['Cocoa_CIGS39017.csv', 'Cocoa_CIGS8-001.csv']),
    'a-Si':        ('#B39DDB', ['Cocoa_aSiMicro03036.csv', 'Cocoa_aSiTandem72-46.csv',
                                'Cocoa_aSiTriple28324.csv']),
}


def leer_poa(path):
    """Serie POA CMP22 (W/m2) indexada por timestamp, streaming línea a línea."""
    tiempos, valores = [], []
    with open(path, 'r', encoding='utf-8') as f:
        for _ in range(3):
            f.readline()
        for row in csv.reader(f):
            if len(row) < 2:
                continue
            try:
                v = float(row[1])
            except ValueError:
                continue
            if v < 0:  # descarta sentinelas -9999 y negativos
                continue
            try:
                t = datetime.strptime(row[0], '%Y-%m-%dT%H:%M:%S')
            except ValueError:
                continue
            tiempos.append(t)
            valores.append(v)
    return pd.Series(valores, index=pd.DatetimeIndex(tiempos))


def main():
    fig, ax = plt.subplots(figsize=(12.6, 6.4))
    total_validos = 0
    suaves = []
    for familia, (color, archivos) in GRUPOS.items():
        for nombre in archivos:
            s = leer_poa(os.path.join(BASE, nombre))
            total_validos += len(s)
            diaria = s.resample('D').median()
            suave = diaria.rolling(7, center=True, min_periods=1).mean()
            suaves.append(suave)
            ax.plot(suave.index, suave.values, color=color, linewidth=1.3, alpha=0.75)
            print(f"  {nombre}: {len(s):,} registros válidos")

    mediana_global = pd.concat(suaves, axis=1).median(axis=1)
    ax.plot(mediana_global.index, mediana_global.values, color='#FFFFFF',
            linewidth=1.6, alpha=0.7)

    ax.set_title('Irradiancia POA — piranómetro CMP22 (11 módulos, Cocoa NREL)\n'
                 'Mediana diaria suavizada a 7 días por archivo',
                 fontsize=16, fontweight='bold', pad=14)
    ax.set_xlabel('Fecha de medición (Cocoa, 2011–2012)', fontsize=13, labelpad=8)
    ax.set_ylabel('POA CMP22 (W/m²)', fontsize=13, labelpad=8)
    ax.tick_params(labelsize=12)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.grid(True, linestyle=':', alpha=0.5)
    ax.set_ylim(bottom=0)

    handles = [Line2D([0], [0], color=c, lw=3) for _, (c, _) in GRUPOS.items()]
    handles.append(Line2D([0], [0], color='#FFFFFF', lw=3))
    etiquetas = list(GRUPOS.keys()) + ['Mediana global']
    ax.legend(handles, etiquetas, fontsize=12, loc='lower center',
              ncol=3, framealpha=0.25)

    fig.tight_layout()
    out = 'output/Extra_Resultados/poa_irradiance_cmp22.png'
    fig.savefig(out, transparent=True, dpi=150, bbox_inches='tight')
    print(f"Registros válidos totales: {total_validos:,}")
    print(f"Gráfico guardado en: {out}")


if __name__ == '__main__':
    main()
