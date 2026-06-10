import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def generate_infographic():
    # Setup dark premium theme
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(10, 8.5), dpi=300)
    ax.axis('off')
    
    # Background color
    fig.patch.set_facecolor('#0d0d1a')
    ax.set_facecolor('#0d0d1a')
    
    # Title
    ax.text(5.0, 8.0, "EMULACIÓN GEOGRÁFICA Y COMPARATIVA DE RECURSO SOLAR", 
            color='#E8A838', fontsize=16, fontweight='bold', ha='center', va='center')
    ax.text(5.0, 7.6, "Filtro de Desfase Estacional (+6 Meses) de Florida (EE.UU.) a Atacama (Chile)", 
            color='#A0A0C0', fontsize=11, style='italic', ha='center', va='center')
    
    # Draw Left Globe: Florida
    # Coordinates of Americas outline for Florida Globe (lon0 = -80, lat0 = 25)
    # R=1.2, centered at (2.2, 5.2)
    cx1, cy1, R1 = 2.2, 5.2, 1.2
    
    # Outer circle representing globe
    globe1 = patches.Circle((cx1, cy1), R1, facecolor='#111129', edgecolor='#007ACC', linewidth=3, zorder=2)
    ax.add_patch(globe1)
    # Glow effect
    for r in np.linspace(R1, R1+0.15, 10):
        glow = patches.Circle((cx1, cy1), r, facecolor='none', edgecolor='#007ACC', alpha=0.08/(r-R1+0.1), zorder=1)
        ax.add_patch(glow)
        
    # Draw Right Globe: Atacama
    # Coordinates of Americas outline for Atacama Globe (lon0 = -68, lat0 = -23)
    # R=1.2, centered at (7.8, 5.2)
    cx2, cy2, R2 = 7.8, 5.2, 1.2
    
    globe2 = patches.Circle((cx2, cy2), R2, facecolor='#111129', edgecolor='#E8A838', linewidth=3, zorder=2)
    ax.add_patch(globe2)
    # Glow effect
    for r in np.linspace(R2, R2+0.15, 10):
        glow = patches.Circle((cx2, cy2), r, facecolor='none', edgecolor='#E8A838', alpha=0.08/(r-R2+0.1), zorder=1)
        ax.add_patch(glow)

    # Simplified coastlines of Americas
    # (lon, lat) points
    americas = [
        # North America
        (-160, 65), (-120, 60), (-120, 50), (-125, 48), (-120, 35), (-115, 30), (-110, 22), (-105, 20),
        (-100, 18), (-95, 15), (-90, 14), (-85, 10), (-82, 8), 
        # South America
        (-77, 7), (-81, -5), (-80, -15), (-72, -35), (-74, -45), (-72, -55), (-65, -55), (-60, -45),
        (-45, -23), (-35, -6), (-40, 5), (-50, 10), (-60, 10), (-70, 10), (-75, 12), (-80, 9),
        # Central America & Gulf
        (-83, 10), (-88, 15), (-97, 20), (-97, 26), (-90, 30), (-84, 30),
        # Florida & East Coast
        (-81, 25), (-80, 28), (-81, 31), (-75, 35), (-70, 42), (-65, 45), (-60, 50), (-70, 60), (-80, 65),
        (-100, 70), (-120, 70), (-140, 70), (-160, 65)
    ]
    
    # Draw parallels & meridians & coastlines on Globe 1
    # lon0 = -80, lat0 = 25
    def project_and_draw(ax, cx, cy, R, lon0, lat0, color, zorder=3):
        # Grid lines
        # Parallels
        for lat in [-60, -30, 0, 30, 60]:
            lons = np.linspace(-180, 180, 100)
            x_pts, y_pts = [], []
            for ln in lons:
                x, y, vis = project_point(ln, lat, lon0, lat0, R, cx, cy)
                if vis:
                    x_pts.append(x)
                    y_pts.append(y)
                else:
                    if x_pts:
                        ax.plot(x_pts, y_pts, color='#2c2c48', linewidth=0.8, zorder=zorder-1)
                        x_pts, y_pts = [], []
            if x_pts:
                ax.plot(x_pts, y_pts, color='#2c2c48', linewidth=0.8, zorder=zorder-1)
                
        # Meridians
        for lon in [-150, -120, -90, -60, -30, 0]:
            lats = np.linspace(-80, 80, 100)
            x_pts, y_pts = [], []
            for lt in lats:
                x, y, vis = project_point(lon, lt, lon0, lat0, R, cx, cy)
                if vis:
                    x_pts.append(x)
                    y_pts.append(y)
                else:
                    if x_pts:
                        ax.plot(x_pts, y_pts, color='#2c2c48', linewidth=0.8, zorder=zorder-1)
                        x_pts, y_pts = [], []
            if x_pts:
                ax.plot(x_pts, y_pts, color='#2c2c48', linewidth=0.8, zorder=zorder-1)
        
        # Coastline
        x_coast, y_coast = [], []
        for lon, lat in americas:
            x, y, vis = project_point(lon, lat, lon0, lat0, R, cx, cy)
            if vis:
                x_coast.append(x)
                y_coast.append(y)
            else:
                if x_coast:
                    ax.plot(x_coast, y_coast, color='#44446b', linewidth=1.5, zorder=zorder)
                    x_coast, y_coast = [], []
        if x_coast:
            ax.plot(x_coast, y_coast, color='#44446b', linewidth=1.5, zorder=zorder)
            
    def project_point(lon, lat, lon0, lat0, R, cx, cy):
        lam = np.radians(lon)
        phi = np.radians(lat)
        lam0 = np.radians(lon0)
        phi0 = np.radians(lat0)
        
        # Distance from center of projection
        cos_c = np.sin(phi0) * np.sin(phi) + np.cos(phi0) * np.cos(phi) * np.cos(lam - lam0)
        visible = cos_c >= 0
        
        x = R * np.cos(phi) * np.sin(lam - lam0)
        y = R * (np.cos(phi0) * np.sin(phi) - np.sin(phi0) * np.cos(phi) * np.cos(lam - lam0))
        
        return cx + x, cy + y, visible

    project_and_draw(ax, cx1, cy1, R1, -80, 25, '#007ACC')
    project_and_draw(ax, cx2, cy2, R2, -68, -23, '#E8A838')
    
    # Highlight locations
    # Cocoa, FL: 28.38 N, 80.74 W
    xf1, yf1, vis1 = project_point(-80.74, 28.38, -80, 25, R1, cx1, cy1)
    if vis1:
        ax.scatter(xf1, yf1, color='#00FFCC', edgecolors='white', s=120, zorder=10, label='Florida, USA')
        ax.text(xf1 - 0.15, yf1 + 0.05, "Cocoa, FL\n(28.4° N)", color='#00FFCC', fontsize=9, fontweight='bold', ha='right', va='center', zorder=11)
        
    # San Pedro de Atacama: 22.91 S, 68.20 W
    xa2, ya2, vis2 = project_point(-68.20, -22.91, -68, -23, R2, cx2, cy2)
    if vis2:
        ax.scatter(xa2, ya2, color='#FF8C00', edgecolors='white', s=120, zorder=10, label='Atacama, Chile')
        ax.text(xa2 - 0.2, ya2 - 0.35, "San Pedro de Atacama\n(22.9° S)", color='#FF8C00', fontsize=9, fontweight='bold', ha='right', zorder=11)
        
    # Draw Central Arrow representing translation
    # Curve arrow from (cx1 + 1.3, cy1) to (cx2 - 1.3, cy2)
    arrow_x1 = cx1 + R1 + 0.1
    arrow_x2 = cx2 - R2 - 0.1
    arrow_y = cy1
    
    # Draw curved arrow using fancy arrow patch
    arrow = patches.FancyArrowPatch((arrow_x1, arrow_y), (arrow_x2, arrow_y),
                                    connectionstyle="arc3,rad=-0.15",
                                    arrowstyle="Simple,tail_width=2,head_width=8,head_length=10",
                                    color='#E8A838', lw=1.5, zorder=5)
    ax.add_patch(arrow)
    
    # Text on Arrow
    ax.text((arrow_x1 + arrow_x2)/2, arrow_y + 0.45, "Filtro de Traslación Temporal y Estacional\nDesfase de +6 Meses (+182 días)",
            color='#FFC83B', fontsize=10, fontweight='bold', ha='center', va='center',
            bbox=dict(facecolor='#111125', edgecolor='#44446b', boxstyle='round,pad=0.5', alpha=0.9))
    
    # Label hemisphere
    ax.text(cx1, cy1 - R1 - 0.3, "Hemisferio Norte\n(Datos NREL Cocoa Originales)", color='#A0A0C0', fontsize=9, ha='center')
    ax.text(cx2, cy2 - R2 - 0.3, "Hemisferio Sur\n(Emulación Atacama 2026)", color='#A0A0C0', fontsize=9, ha='center')
    
    # Divider Line
    divider = patches.ConnectionPatch((0.5, 3.2), (9.5, 3.2), "data", "data", color='#2c2c48', lw=1.5, ls='--')
    ax.add_artist(divider)
    
    # Information Box: Title
    ax.text(5.0, 2.9, "COMPARACIÓN METEOROLÓGICA Y VARIABLES SOLARES", 
            color='#E8A838', fontsize=12, fontweight='bold', ha='center', va='center')
    
    # side-by-side comparison tables/panels
    # Panel Florida
    panel_f = patches.Rectangle((0.5, 0.3), 4.2, 2.3, facecolor='#111129', edgecolor='#007ACC', linewidth=1.5, zorder=2)
    ax.add_patch(panel_f)
    
    # Panel Atacama
    panel_a = patches.Rectangle((5.3, 0.3), 4.2, 2.3, facecolor='#111129', edgecolor='#E8A838', linewidth=1.5, zorder=2)
    ax.add_patch(panel_a)
    
    # Florida details
    ax.text(0.7, 2.3, "Cocoa, Florida (Original)", color='#007ACC', fontsize=11, fontweight='bold')
    f_details = [
        "• Clima: Subtropical Húmedo (Marítimo)",
        "• Altitud: 10 m.s.n.m. (Nivel del Mar)",
        "• Irradiancia Difusa: Alta (~35% - 45%)",
        "  debido a alta humedad y nubosidad.",
        "• DNI Máximo: ~950 W/m² (Atenuado)",
        "• Nubosidad: Frecuente / Convectiva",
        "• Tc Pico (Celda): ~55°C - 60°C"
    ]
    for i, line in enumerate(f_details):
        ax.text(0.7, 2.0 - i*0.24, line, color='#CCCCCC', fontsize=9, va='center')
        
    # Atacama details
    ax.text(5.5, 2.3, "San Pedro de Atacama (Emulado)", color='#E8A838', fontsize=11, fontweight='bold')
    a_details = [
        "• Clima: Hiperárido (Desértico Extremo)",
        "• Altitud: 2400 m.s.n.m. (Atmósfera Delgada)",
        "• Irradiancia Difusa: Muy Baja (~10% - 15%)",
        "  cielos permanentemente limpios.",
        "• DNI Máximo: >1250 W/m² (Extremo)",
        "• Nubosidad: Casi nula durante el año",
        "• Tc Pico (Celda): ~65°C - 70°C (Alto estrés)"
    ]
    for i, line in enumerate(a_details):
        ax.text(5.5, 2.0 - i*0.24, line, color='#CCCCCC', fontsize=9, va='center')
        
    # Save fig
    output_path = 'output/Extra_Resultados/geo_emulation_map.png'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, facecolor='#0d0d1a', bbox_inches='tight', pad_inches=0.2)
    plt.close()
    print(f"Successfully generated new clean geographic emulation map at: {output_path}")

if __name__ == '__main__':
    generate_infographic()
