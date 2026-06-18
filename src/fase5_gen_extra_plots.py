import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pvlib
import json
import os

# --- Configurar estilo dark mode premium para Matplotlib ---
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

def gen_extra_results():
    # 1. Cargar parámetros de De Soto
    if not os.path.exists('temp/parametros_desoto.json'):
        print("Error: No se encontró temp/parametros_desoto.json.")
        return

    with open('temp/parametros_desoto.json', 'r') as f:
        params = json.load(f)
    
    file_msi = 'output/Fase2_Resultados/Simulacion_mSi_Atacama.csv'
    file_hit = 'output/Fase2_Resultados/Simulacion_HIT_Atacama.csv'
    
    if not os.path.exists(file_msi) or not os.path.exists(file_hit):
        print("Error: No se encontraron los archivos de simulación.")
        return

    df_msi = pd.read_csv(file_msi)
    df_hit = pd.read_csv(file_hit)
    
    output_dir = 'output/Extra_Resultados'
    os.makedirs(output_dir, exist_ok=True)
    
    # --- GRÁFICO 1: Curvas I-V y P-V en SRC ---
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14.7, 7.0))
    
    for mod in ['mSi', 'HIT']:
        p = params[mod]
        V_pts = np.linspace(0, p['Voc_ref'], 100)
        I_pts = []
        for v in V_pts:
            i = pvlib.pvsystem.i_from_v(
                resistance_shunt=p['Rsh_ref'], 
                resistance_series=p['Rs_ref'], 
                nNsVth=p['a_ref'], 
                voltage=v, 
                saturation_current=p['Io_ref'], 
                photocurrent=p['IL_ref'], 
                method='lambertw'
            )
            I_pts.append(max(0, float(i)))
        
        I_pts = np.array(I_pts)
        color = '#007ACC' if mod == 'mSi' else '#E8A838'
        label_name = 'm-Si (SRC)' if mod == 'mSi' else 'HIT (SRC)'
        ax1.plot(V_pts, I_pts, label=label_name, linewidth=3.5, color=color)
        ax1.scatter(p['Vmp_ref'], p['Imp_ref'], color='red', s=60, zorder=5, edgecolor='white')
        
        P_pts = V_pts * I_pts
        ax2.plot(V_pts, P_pts, label=label_name, linewidth=3.5, color=color)
        ax2.scatter(p['Vmp_ref'], p['Pmp_ref'], color='red', s=60, zorder=5, edgecolor='white')
    
    ax1.set_title('Curvas I-V en Condiciones SRC', fontsize=14, fontweight='bold', pad=15)
    ax1.set_xlabel('Voltaje (V)', fontsize=12)
    ax1.set_ylabel('Corriente (A)', fontsize=12)
    ax1.legend(fontsize=11)
    ax1.grid(True, linestyle=':', alpha=0.5)
    
    ax2.set_title('Curvas P-V en Condiciones SRC', fontsize=14, fontweight='bold', pad=15)
    ax2.set_xlabel('Voltaje (V)', fontsize=12)
    ax2.set_ylabel('Potencia (W)', fontsize=12)
    ax2.legend(fontsize=11)
    ax2.grid(True, linestyle=':', alpha=0.5)
    ax2.set_ylim(0, 250)
    
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'curvas_iv_pv_src.png'), transparent=True, dpi=150, bbox_inches='tight')
    plt.close()
    
    # --- GRÁFICO 2: Perfil de un Día Despejado ---
    df_msi['time'] = pd.to_datetime(df_msi['time'], utc=True)
    # Volver a hora local de Atacama (UTC-4) y quitar tz: matplotlib grafica
    # los timestamps tz-aware en UTC, corriendo el mediodía solar +4 h.
    df_msi['time'] = df_msi['time'].dt.tz_convert('Etc/GMT+4').dt.tz_localize(None)
    df_msi = df_msi.sort_values('time')
    
    # Día despejado representativo del verano emulado (28 de enero de 2026:
    # POA ~990 W/m² con la mínima variabilidad nubosa del periodo estival)
    dia_ejemplo = df_msi[(df_msi['time'].dt.month == 1) & (df_msi['time'].dt.day == 28)].copy()
    
    if not dia_ejemplo.empty:
        fig, ax1 = plt.subplots(figsize=(14, 6.7))
        ax2 = ax1.twinx()
        
        ax1.plot(dia_ejemplo['time'], dia_ejemplo['poa_global'], color='#E8A838', label='Irradiancia POA', linewidth=2.5)
        ax2.plot(dia_ejemplo['time'], dia_ejemplo['temp_cell'], color='#FF4C4C', label='Temp. Celda', linewidth=2.5, alpha=0.8)
        
        ax1.set_xlabel('Hora del Día (28 Ene 2026, hora local Atacama)', fontsize=12)
        ax1.set_ylabel('Irradiancia (W/m2)', color='#E8A838', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Temperatura (°C)', color='#FF4C4C', fontsize=12, fontweight='bold')
        ax1.tick_params(axis='y', labelcolor='#E8A838')
        ax2.tick_params(axis='y', labelcolor='#FF4C4C')
        
        # Combinar leyendas de ejes primario y secundario
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right', fontsize=11, framealpha=0.7)
        
        import matplotlib.dates as mdates
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        ax1.grid(True, linestyle=':', alpha=0.5)
        
        fig.tight_layout()
        plt.savefig(os.path.join(output_dir, 'perfil_dia_tipico.png'), transparent=True, dpi=150)
        plt.close()
    
    # --- GRÁFICO 3: Performance Ratio Mensual Comparativo ---
    df_msi_time = df_msi.copy()
    df_hit_time = df_hit.copy()
    df_msi_time['time'] = pd.to_datetime(df_msi_time['time'])
    df_hit_time['time'] = pd.to_datetime(df_hit_time['time'])
    df_msi_time.set_index('time', inplace=True)
    df_hit_time.set_index('time', inplace=True)
    
    pr_msi = df_msi_time['pmp_teorica'].resample('ME').sum() / df_msi_time['p_ideal_stc'].resample('ME').sum()
    pr_hit = df_hit_time['pmp_teorica'].resample('ME').sum() / df_hit_time['p_ideal_stc'].resample('ME').sum()
    
    plt.figure(figsize=(14, 6.7))
    plt.plot(range(1, 13), pr_msi.values, marker='o', label='PR m-Si', linewidth=3, color='#007ACC', markersize=8)
    plt.plot(range(1, 13), pr_hit.values, marker='o', label='PR HIT', linewidth=3, color='#E8A838', markersize=8)
    plt.xlabel('Mes', fontsize=12)
    plt.ylabel('Performance Ratio', fontsize=12)
    plt.ylim(0.80, 0.96)
    plt.xticks(range(1, 13), ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'])
    plt.legend(fontsize=11)
    plt.grid(True, linestyle=':', alpha=0.5)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'pr_mensual_comparativo.png'), transparent=True, dpi=150)
    plt.close()
    
    # --- GRÁFICO 4: Análisis de Degradación Térmica ---
    plt.figure(figsize=(10, 6))
    for mod, df in [('mSi', df_msi), ('HIT', df_hit)]:
        p_stc = params[mod]['Pmp_ref']
        mask = (df['poa_global'] > 400) & (df['pmp_teorica'] > 0)
        subset = df[mask]
        eff_norm = (subset['pmp_teorica'] / (subset['poa_global'] / 1000)) / p_stc
        color = '#007ACC' if mod == 'mSi' else '#E8A838'
        label_name = 'm-Si' if mod == 'mSi' else 'HIT'
        plt.scatter(subset['temp_cell'], eff_norm, alpha=0.06, label=label_name, s=5, color=color)
        
    plt.xlabel('Temperatura de Celda (°C)', fontsize=15, labelpad=10)
    plt.ylabel('Potencia Normalizada', fontsize=15, labelpad=10)
    plt.xticks(fontsize=13)
    plt.yticks(fontsize=13)
    leg = plt.legend(fontsize=13)
    for lh in leg.legend_handles:
        lh.set_alpha(1.0)
    plt.grid(True, linestyle=':', alpha=0.5)
    plt.ylim(0.75, 1.05)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'degradacion_termica_scatter.png'), transparent=True, dpi=150, bbox_inches='tight')
    plt.close()

    # --- GRÁFICO 5: Modificadores Ópticos APLICADOS (IAM y espectral) ---
    # Panel izq: respuesta angular K_τα(θ) del modelo físico (Snell-Bouguer).
    # Panel der: factor espectral M vs masa de aire para distintos PW (agua
    # precipitable), evaluado con el modelo First Solar de pvlib.
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(14.7, 6.2))

    aoi = np.linspace(0, 90, 181)
    iam = pvlib.iam.physical(aoi, n=1.526, K=4.0, L=0.002)
    axL.plot(aoi, iam, color='#00D2FF', linewidth=3.5, label=r'$K_{\tau\alpha}(\theta)$ (físico)')
    axL.axvspan(0, 60, color='#2ECC71', alpha=0.10, label='Rango operativo típico (<60°)')
    for ang in (60, 75, 85):
        axL.scatter([ang], [float(pvlib.iam.physical(ang))], s=55, color='#FF5E3A', zorder=5, edgecolor='white')
        axL.annotate(f'{float(pvlib.iam.physical(ang)):.2f}', (ang, float(pvlib.iam.physical(ang))),
                     textcoords='offset points', xytext=(-6, 10), color='#FF5E3A', fontsize=11, fontweight='bold')
    axL.set_title('Modificador por ángulo de incidencia (IAM)', fontsize=14, fontweight='bold', pad=12)
    axL.set_xlabel('Ángulo de incidencia θ (°)', fontsize=12)
    axL.set_ylabel(r'$K_{\tau\alpha}=\tau(\theta)/\tau(0)$', fontsize=12)
    axL.set_xlim(0, 90); axL.set_ylim(0, 1.05)
    axL.grid(True, linestyle=':', alpha=0.5); axL.legend(fontsize=11, loc='lower left')

    am = np.linspace(1, 5, 100)
    for pw, c in [(0.5, '#E8A838'), (1.0, '#00D2FF'), (2.0, '#FF5E3A')]:
        M = pvlib.spectrum.spectral_factor_firstsolar(np.full_like(am, pw), am, module_type='monosi')
        axR.plot(am, M, linewidth=3, color=c, label=f'PW = {pw:.1f} cm')
    axR.axhline(1.0, color='#9AA5B1', linestyle='--', linewidth=1.2, alpha=0.7)
    axR.set_title('Factor espectral M (First Solar, c-Si)', fontsize=14, fontweight='bold', pad=12)
    axR.set_xlabel('Masa de aire absoluta AM', fontsize=12)
    axR.set_ylabel('M (corrección espectral)', fontsize=12)
    axR.set_ylim(0.92, 1.06)
    axR.grid(True, linestyle=':', alpha=0.5); axR.legend(fontsize=11, title='Agua precipitable')

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'modificadores_opticos.png'), transparent=True, dpi=150, bbox_inches='tight')
    plt.close()

    print("Gráficos reconstruidos (IV Curves, Perfil, PR Comparativo, Degradación y Modificadores ópticos IAM/AM).")

if __name__ == "__main__":
    gen_extra_results()
