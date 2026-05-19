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
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
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
    plt.savefig(os.path.join(output_dir, 'curvas_iv_pv_src.png'), transparent=True, dpi=150)
    plt.close()
    
    # --- GRÁFICO 2: Perfil de un Día Despejado ---
    df_msi['time'] = pd.to_datetime(df_msi['time'])
    df_msi = df_msi.sort_values('time')
    
    # Elegir un día representativo (ej: 15 de Febrero)
    dia_ejemplo = df_msi[(df_msi['time'].dt.month == 2) & (df_msi['time'].dt.day == 15)].copy()
    
    if not dia_ejemplo.empty:
        fig, ax1 = plt.subplots(figsize=(14, 6.7))
        ax2 = ax1.twinx()
        
        ax1.plot(dia_ejemplo['time'], dia_ejemplo['poa_global'], color='#E8A838', label='Irradiancia POA', linewidth=2.5)
        ax2.plot(dia_ejemplo['time'], dia_ejemplo['temp_cell'], color='#FF4C4C', label='Temp. Celda', linewidth=2.5, alpha=0.8)
        
        ax1.set_xlabel('Hora del Día (15 Feb 2026)', fontsize=12)
        ax1.set_ylabel('Irradiancia (W/m2)', color='#E8A838', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Temperatura (°C)', color='#FF4C4C', fontsize=12, fontweight='bold')
        ax1.tick_params(axis='y', labelcolor='#E8A838')
        ax2.tick_params(axis='y', labelcolor='#FF4C4C')
        
        plt.title('Perfil Dinámico Horario en el Desierto de Atacama', fontsize=14, fontweight='bold', pad=15)
        
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
    plt.title('Performance Ratio Mensual en Atacama (Simulación 2026)', fontsize=14, fontweight='bold', pad=15)
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
        
    plt.title('Análisis de Degradación Térmica: HIT vs m-Si', fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Temperatura de Celda (°C)', fontsize=12)
    plt.ylabel('Potencia Normalizada', fontsize=12)
    plt.legend(fontsize=11)
    plt.grid(True, linestyle=':', alpha=0.5)
    plt.ylim(0.75, 1.05)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'degradacion_termica_scatter.png'), transparent=True, dpi=150)
    plt.close()

    print(f"Ciclo 3: Gráficos reconstruidos (IV Curves, Perfil, PR Comparativo y Degradación corregidos en Dark Mode y Transparentes).")

if __name__ == "__main__":
    gen_extra_results()
