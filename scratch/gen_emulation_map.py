# -*- coding: utf-8 -*-
"""
Mapa de emulación geográfica v2 — formato WIDE para slide completo.
Solo los dos globos + flecha de traslación, con tipografía grande.
La comparación meteorológica vive ahora como paneles nativos del deck.
Salida: output/Extra_Resultados/geo_emulation_map.png
"""
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

BG = '#0d0d1a'

def project_point(lon, lat, lon0, lat0, R, cx, cy):
    lam, phi = np.radians(lon), np.radians(lat)
    lam0, phi0 = np.radians(lon0), np.radians(lat0)
    cos_c = np.sin(phi0)*np.sin(phi) + np.cos(phi0)*np.cos(phi)*np.cos(lam-lam0)
    x = R*np.cos(phi)*np.sin(lam-lam0)
    y = R*(np.cos(phi0)*np.sin(phi) - np.sin(phi0)*np.cos(phi)*np.cos(lam-lam0))
    return cx+x, cy+y, cos_c >= 0

AMERICAS = [
    (-160,65),(-120,60),(-120,50),(-125,48),(-120,35),(-115,30),(-110,22),(-105,20),
    (-100,18),(-95,15),(-90,14),(-85,10),(-82,8),
    (-77,7),(-81,-5),(-80,-15),(-72,-35),(-74,-45),(-72,-55),(-65,-55),(-60,-45),
    (-45,-23),(-35,-6),(-40,5),(-50,10),(-60,10),(-70,10),(-75,12),(-80,9),
    (-83,10),(-88,15),(-97,20),(-97,26),(-90,30),(-84,30),
    (-81,25),(-80,28),(-81,31),(-75,35),(-70,42),(-65,45),(-60,50),(-70,60),(-80,65),
    (-100,70),(-120,70),(-140,70),(-160,65),
]

def draw_globe(ax, cx, cy, R, lon0, lat0, edge):
    ax.add_patch(patches.Circle((cx,cy), R, facecolor='#111129', edgecolor=edge, linewidth=4, zorder=2))
    for r in np.linspace(R, R+0.22, 10):
        ax.add_patch(patches.Circle((cx,cy), r, facecolor='none', edgecolor=edge,
                                    alpha=0.08/(r-R+0.1)*0.1, zorder=1))
    for lat in [-60,-30,0,30,60]:
        xs, ys = [], []
        for ln in np.linspace(-180,180,120):
            x,y,v = project_point(ln, lat, lon0, lat0, R, cx, cy)
            if v: xs.append(x); ys.append(y)
            elif xs: ax.plot(xs, ys, color='#2c2c48', lw=1.0, zorder=2.5); xs, ys = [], []
        if xs: ax.plot(xs, ys, color='#2c2c48', lw=1.0, zorder=2.5)
    for lon in [-150,-120,-90,-60,-30,0]:
        xs, ys = [], []
        for lt in np.linspace(-80,80,120):
            x,y,v = project_point(lon, lt, lon0, lat0, R, cx, cy)
            if v: xs.append(x); ys.append(y)
            elif xs: ax.plot(xs, ys, color='#2c2c48', lw=1.0, zorder=2.5); xs, ys = [], []
        if xs: ax.plot(xs, ys, color='#2c2c48', lw=1.0, zorder=2.5)
    xs, ys = [], []
    for lon, lat in AMERICAS:
        x,y,v = project_point(lon, lat, lon0, lat0, R, cx, cy)
        if v: xs.append(x); ys.append(y)
        elif xs: ax.plot(xs, ys, color='#5a5a85', lw=2.0, zorder=3); xs, ys = [], []
    if xs: ax.plot(xs, ys, color='#5a5a85', lw=2.0, zorder=3)

def generate_infographic():
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(14.0, 6.3), dpi=220, facecolor=BG)
    ax = fig.add_axes([0,0,1,1]); ax.axis('off')
    ax.set_xlim(0,14); ax.set_ylim(0,6.3); ax.set_facecolor(BG)

    cx1, cy1, R = 3.1, 3.05, 2.15
    cx2, cy2 = 10.9, 3.05
    draw_globe(ax, cx1, cy1, R, -80, 25, '#007ACC')
    draw_globe(ax, cx2, cy2, R, -68, -23, '#E8A838')

    # Marcadores de sitio
    xf, yf, _ = project_point(-80.74, 28.38, -80, 25, R, cx1, cy1)
    ax.scatter(xf, yf, color='#00FFCC', edgecolors='white', s=260, zorder=10)
    ax.text(xf-0.28, yf+0.34, "Cocoa, FL", color='#00FFCC', fontsize=19,
            fontweight='bold', ha='right', zorder=11)
    ax.text(xf-0.28, yf-0.08, "28.4° N · 12 m", color='#00FFCC', fontsize=14,
            ha='right', zorder=11)

    xa, ya, _ = project_point(-68.20, -22.91, -68, -23, R, cx2, cy2)
    ax.scatter(xa, ya, color='#FF8C00', edgecolors='white', s=260, zorder=10)
    ax.text(xa+0.32, ya+0.30, "San Pedro de Atacama", color='#FF8C00', fontsize=19,
            fontweight='bold', ha='left', zorder=11)
    ax.text(xa+0.32, ya-0.12, "22.9° S · 2,400 m", color='#FF8C00', fontsize=14,
            ha='left', zorder=11)

    # Flecha central de traslación
    a1, a2, ay = cx1+R+0.15, cx2-R-0.15, 3.05
    ax.add_patch(patches.FancyArrowPatch((a1,ay),(a2,ay), connectionstyle="arc3,rad=-0.18",
                 arrowstyle="Simple,tail_width=4,head_width=16,head_length=18",
                 color='#E8A838', lw=2, zorder=5))
    ax.text((a1+a2)/2, ay+1.18, "DESFASE  +6 MESES  (+182 días)", color='#FFC83B',
            fontsize=20, fontweight='bold', ha='center', va='center', zorder=6,
            bbox=dict(facecolor='#111125', edgecolor='#E8A838', boxstyle='round,pad=0.55', lw=1.5))
    ax.text((a1+a2)/2, ay+0.52, "+ proyección al año 2026\n+ reescritura de metadatos de sitio",
            color='#C9D1D9', fontsize=13.5, ha='center', va='center', zorder=6)

    # Etiquetas de hemisferio (bajo cada globo)
    ax.text(cx1, cy1-R-0.42, "HEMISFERIO NORTE", color='#00D2FF', fontsize=16,
            fontweight='bold', ha='center')
    ax.text(cx1, cy1-R-0.78, "Datos NREL Cocoa originales (2011–2012)", color='#A0A0C0',
            fontsize=12.5, ha='center')
    ax.text(cx2, cy2-R-0.42, "HEMISFERIO SUR", color='#F1C40F', fontsize=16,
            fontweight='bold', ha='center')
    ax.text(cx2, cy2-R-0.78, "Emulación San Pedro de Atacama (año 2026)", color='#A0A0C0',
            fontsize=12.5, ha='center')

    # Nota de coherencia física (arriba, entre globos)
    ax.text((a1+a2)/2, 5.75, "Invierno ⇄ Verano: los solsticios quedan físicamente alineados",
            color='#9AA5B1', fontsize=12.5, style='italic', ha='center')

    out = 'output/Extra_Resultados/geo_emulation_map.png'
    os.makedirs(os.path.dirname(out), exist_ok=True)
    plt.savefig(out, facecolor=BG, bbox_inches='tight', pad_inches=0.15)
    plt.close()
    print('OK ->', out)

if __name__ == '__main__':
    generate_infographic()
