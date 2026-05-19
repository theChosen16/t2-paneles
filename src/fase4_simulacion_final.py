import pandas as pd
import numpy as np
import pvlib
import json
import matplotlib.pyplot as plt
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

def simular_desempeno(module_name, params, df):
    print(f"--- Simulación Final para {module_name} ---")
    
    # 1. Parámetros De Soto
    IL_ref = params['IL_ref']
    Io_ref = params['Io_ref']
    a_ref = params['a_ref']
    Rs_ref = params['Rs_ref']
    Rsh_ref = params['Rsh_ref']
    alpha_isc = params['alpha_isc']
    beta_voc = params['beta_voc']
    Ns = params['Ns']
    Eg_ref = 1.121 # Silicio
    
    # 2. Simular Pmp usando pvlib.pvsystem.singlediode
    print("Calculando potencia teórica paso a paso...")
    
    # Ajustar parámetros a condiciones de operación (De Soto)
    # IL = G/Gref * (IL_ref + alpha * (Tc - Tref))
    # a = a_ref * (Tc / Tref)
    # Io = Io_ref * (Tc/Tref)**3 * exp(Eg/k * (1/Tref - 1/Tc))
    # Rsh = Rsh_ref * (Gref / G)
    # Rs = Rs_ref
    
    T_ref = 25 + 273.15
    Tc_k = df['temp_cell'] + 273.15
    G_ratio = df['poa_global'] / 1000
    
    # pvlib.pvsystem.calcparams_desoto hace esto automáticamente
    IL, Io, Rs, Rsh, a = pvlib.pvsystem.calcparams_desoto(
        df['poa_global'],
        df['temp_cell'],
        alpha_sc=alpha_isc,
        a_ref=a_ref,
        I_L_ref=IL_ref,
        I_o_ref=Io_ref,
        R_sh_ref=Rsh_ref,
        R_s=Rs_ref,
        EgRef=Eg_ref,
        dEgdT=-0.0002677
    )
    
    # Resolver diodo para cada punto
    out = pvlib.pvsystem.singlediode(IL, Io, Rs, Rsh, a)
    df['pmp_teorica'] = out['p_mp']
    
    # 3. Cálculo de Métricas
    # Energía Real (tomamos la medida pmp del CSV que ya venía en el archivo)
    # Nota: Usamos pmp_teorica como la producción simulada en Atacama
    # La pmp_medida del archivo es la de Florida. Para Atacama, nuestro "resultado" es pmp_teorica.
    
    # Performance Ratio (PR)
    # Encontramos P_STC resolviendo el modelo a 1000W/m2 y 25C
    IL_s, Io_s, Rs_s, Rsh_s, a_s = pvlib.pvsystem.calcparams_desoto(
        1000, 25, alpha_sc=alpha_isc, a_ref=a_ref, I_L_ref=IL_ref, I_o_ref=Io_ref, R_sh_ref=Rsh_ref, R_s=Rs_ref
    )
    p_stc_val = pvlib.pvsystem.singlediode(IL_s, Io_s, Rs_s, Rsh_s, a_s)['p_mp']
    
    df['p_ideal_stc'] = G_ratio * p_stc_val
    
    # PR Mensual
    pr_monthly = df['pmp_teorica'].resample('ME').sum() / df['p_ideal_stc'].resample('ME').sum()
    
    # 4. Gráficos
    output_dir = 'output/Fase2_Resultados'
    os.makedirs(output_dir, exist_ok=True)
    
    plt.figure(figsize=(10, 5))
    plot_color = '#E8A838' if module_name == 'HIT' else '#007ACC'
    pr_monthly.plot(kind='line', marker='o', color=plot_color, linewidth=2)
    plt.title(f'Performance Ratio Mensual - {module_name} (Atacama 2026)', fontsize=13, fontweight='bold', pad=15)
    plt.ylabel('PR', fontsize=11)
    plt.ylim(0.7, 1.0)
    plt.grid(True, linestyle=':', alpha=0.5)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f'pr_mensual_{module_name}.png'), transparent=True, dpi=150)
    plt.close()
    
    # Comparación P_medida vs P_teorica (Scatter)
    plt.figure(figsize=(10, 7.5))
    scatter_color = '#E8A838' if module_name == 'HIT' else '#007ACC'
    plt.scatter(df['pmp'], df['pmp_teorica'], alpha=0.08, s=3, color=scatter_color, label='Datos Minutales')
    plt.plot([0, df['pmp'].max()], [0, df['pmp'].max()], 'r--', linewidth=2, label='1:1 Relación')
    # plt.title(f'Validación Potencia: Medida vs Simulada - {module_name}', fontsize=12, fontweight='bold', pad=15)
    plt.xlabel('Pmp Medida (Florida) [W]', fontsize=16, labelpad=10)
    plt.ylabel('Pmp Simulada (Atacama) [W]', fontsize=16, labelpad=10)
    plt.xticks(fontsize=13)
    plt.yticks(fontsize=13)
    plt.grid(True, linestyle=':', alpha=0.5)
    leg = plt.legend(fontsize=13)
    for lh in leg.legend_handles:
        lh.set_alpha(1.0)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f'val_scatter_{module_name}.png'), transparent=True, dpi=150, bbox_inches='tight')
    plt.close()
    
    pr_anual = df['pmp_teorica'].sum() / df['p_ideal_stc'].sum()
    print(f"Performance Ratio Anual: {pr_anual:.4f}")
    
    # GUARDAR RESULTADOS DETALLADOS
    res_path = os.path.join(output_dir, f'Simulacion_{module_name}_Atacama.csv')
    df.to_csv(res_path)
    print(f"Resultados guardados en: {res_path}")
    
    return pr_anual

if __name__ == "__main__":
    with open('temp/parametros_desoto.json', 'r') as f:
        all_params = json.load(f)
        
    for mod in ['mSi', 'HIT']:
        path = f'output/Fase1_Resultados/Datos_Fase2_{mod}.csv'
        if os.path.exists(path):
            df = pd.read_csv(path)
            df['time'] = pd.to_datetime(df['time'])
            df.set_index('time', inplace=True)
            simular_desempeno(mod, all_params[mod], df)
