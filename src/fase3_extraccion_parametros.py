import pandas as pd
import numpy as np
from scipy.optimize import fsolve
import matplotlib.pyplot as plt
import os

def extraer_parametros_src(df, module_name):
    print(f"--- Extrayendo Parámetros SRC para {module_name} ---")
    
    # 1. Encontrar coeficientes de temperatura (alpha_Isc y beta_Voc)
    # Filtramos puntos con alta irradiancia para que la varianza sea principalmente térmica
    df_high = df[(df['poa_global'] > 800) & (df['poa_global'] < 1200)].copy()
    
    # Normalizamos Isc a 1000 W/m2 para aislar el efecto térmico
    df_high['isc_norm'] = df_high['isc'] * (1000 / df_high['poa_global'])
    
    # Ajuste lineal: isc_norm = alpha * Tc + const
    slope_i, intercept_i = np.polyfit(df_high['temp_cell'], df_high['isc_norm'], 1)
    alpha_isc = slope_i # A/°C
    
    # Ajuste lineal: voc = beta * Tc + const
    slope_v, intercept_v = np.polyfit(df_high['temp_cell'], df_high['voc'], 1)
    beta_voc = slope_v # V/°C
    
    print(f"Alpha_Isc: {alpha_isc:.6f} A/°C")
    print(f"Beta_Voc: {beta_voc:.6f} V/°C")
    
    # 2. Encontrar punto de referencia SRC (1000 W/m2, 25 °C)
    # Tomamos el promedio de los puntos cerca de 1000 y normalizamos a 25C
    puntos_src = df[(df['poa_global'] > 900) & (df['poa_global'] < 1100)].copy()
    
    # Normalización a SRC (1000 W/m2, 25 °C)
    # IL = Isc en SRC
    t_diff = (25 - puntos_src['temp_cell'])
    g_ratio = (1000 / puntos_src['poa_global'])
    
    isc_src = (puntos_src['isc'] * g_ratio) + alpha_isc * (25 - puntos_src['temp_cell'])
    voc_src = puntos_src['voc'] + beta_voc * (25 - puntos_src['temp_cell'])
    imp_src = (puntos_src['imp'] * g_ratio) # Simplificación inicial
    vmp_src = puntos_src['vmp'] + beta_voc * (25 - puntos_src['temp_cell'])
    
    Isc_ref = isc_src.mean()
    Voc_ref = voc_src.mean()
    Imp_ref = imp_src.mean()
    Vmp_ref = vmp_src.mean()
    Pmp_ref = Vmp_ref * Imp_ref
    
    print(f"Valores SRC calculados:")
    print(f"  Isc_ref: {Isc_ref:.4f} A")
    print(f"  Voc_ref: {Voc_ref:.4f} V")
    print(f"  Imp_ref: {Imp_ref:.4f} A")
    print(f"  Vmp_ref: {Vmp_ref:.4f} V")
    print(f"  Pmp_ref: {Pmp_ref:.4f} W")
    
    # 3. Resolver Modelo de De Soto (5 parámetros) con Optimización
    # Para asegurar Rs > 0 y convergencia, usamos minimize con el error en los 3 puntos clave
    k = 1.380649e-23
    q = 1.60217663e-19
    T_ref = 25 + 273.15
    Ns = 36 if 'mSi' in module_name else 72
    if Voc_ref > 30: Ns = 72
    
    # Forzar alpha_isc positivo si salió negativo (típico 0.05%/°C)
    if alpha_isc <= 0:
        alpha_isc = Isc_ref * 0.0005
    
    def calculate_i(V, p):
        IL, Io, a, Rs, Rsh = p
        # Usamos iteración de punto fijo simple para resolver la ec. implícita de I
        I = IL
        for _ in range(5):
            exponent = (V + I * Rs) / a
            # Clip para evitar overflow en exp
            exponent = np.clip(exponent, -500, 700)
            I = IL - Io * (np.exp(exponent) - 1) - (V + I * Rs) / Rsh
        return I

    def objective(p):
        IL, Io, a, Rs, Rsh = p
        # Error en Voc
        # IL - Io*(exp(Voc/a)-1) - Voc/Rsh = 0
        exp_voc = np.clip(Voc_ref/a, -500, 700)
        e1 = IL - Io * (np.exp(exp_voc) - 1) - Voc_ref / Rsh
        # Error en Isc
        # IL - Io*(exp(Isc*Rs/a)-1) - Isc*Rs/Rsh = Isc
        exp_isc = np.clip(Isc_ref*Rs/a, -500, 700)
        e2 = IL - Io * (np.exp(exp_isc) - 1) - Isc_ref * Rs / Rsh - Isc_ref
        # Error en MPP
        exp_mpp = np.clip((Vmp_ref + Imp_ref * Rs) / a, -500, 700)
        e3 = IL - Io * (np.exp(exp_mpp) - 1) - (Vmp_ref + Imp_ref * Rs) / Rsh - Imp_ref
        
        return (e1**2 + e2**2 + e3**2)

    # Estimaciones iniciales y límites
    a_init = Ns * 1.2 * k * T_ref / q
    IL_init = Isc_ref
    Io_init = Isc_ref * np.exp(-Voc_ref / a_init)
    
    from scipy.optimize import minimize
    res_opt = minimize(objective, [IL_init, Io_init, a_init, 0.01, 1000], 
                      bounds=[(IL_init*0.9, IL_init*1.1), (1e-12, 1e-5), (a_init*0.5, a_init*2), (0.001, 2.0), (100, 10000)])
    
    sol = res_opt.x
    
    params = {
        'IL_ref': sol[0],
        'Io_ref': sol[1],
        'a_ref': sol[2],
        'Rs_ref': sol[3],
        'Rsh_ref': sol[4],
        'alpha_isc': alpha_isc,
        'beta_voc': beta_voc,
        'Ns': Ns,
        'Isc_ref': Isc_ref,
        'Voc_ref': Voc_ref,
        'Imp_ref': Imp_ref,
        'Vmp_ref': Vmp_ref,
        'Pmp_ref': Pmp_ref
    }
    
    print(f"Parámetros De Soto extraídos:")
    for k_v, v in params.items():
        print(f"  {k_v}: {v}")
        
    return params

if __name__ == "__main__":
    import json
    res = {}
    for mod in ['mSi', 'HIT']:
        path = f'output/Fase1_Resultados/Datos_Fase2_{mod}.csv'
        if os.path.exists(path):
            df = pd.read_csv(path)
            res[mod] = extraer_parametros_src(df, mod)
            
    with open('temp/parametros_desoto.json', 'w') as f:
        json.dump(res, f, indent=4)
    print("\nParámetros guardados en temp/parametros_desoto.json")
