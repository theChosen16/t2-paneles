import pandas as pd
import numpy as np
import pvlib
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

def procesar_fase1(file_path, output_dir):
    print(f"--- Procesando Fase 1 para: {file_path} ---")
    
    # 1. Leer Metadatos
    with open(file_path, 'r', encoding='utf-8') as f:
        meta_cols = f.readline().strip().split(',')
        meta_vals = f.readline().strip().split(',')
        
    lat = float(meta_vals[4])
    lon = float(meta_vals[5])
    elevation = float(meta_vals[6])
    tilt = float(meta_vals[7])
    azimuth = float(meta_vals[8])
    tz = 'Etc/GMT+4' # UTC-4
    
    # Crear Location
    location = pvlib.location.Location(lat, lon, tz, elevation, 'San Pedro de Atacama')
    
    # 2. Leer Datos (Saltando metadatos)
    print("Cargando datos usando pandas...")
    # Solo leemos las columnas relevantes para Fase 1 para ahorrar memoria
    # 2. Leer Datos (Lector manual para evitar problemas con filas de longitud variable)
    print("Cargando datos usando lector manual...")
    data = []
    with open(file_path, 'r', encoding='utf-8') as f:
        # Saltar metadatos (líneas 1 y 2) y header (línea 3)
        [f.readline() for _ in range(3)]
        import csv
        reader = csv.reader(f)
        for row in reader:
            if not row: continue
            try:
                # Extraer por índice (0-based)
                data.append({
                    'time': row[0],
                    'isc': float(row[5]),
                    'pmp': float(row[7]),
                    'imp': float(row[9]),
                    'vmp': float(row[11]),
                    'voc': float(row[13]),
                    'temp_air': float(row[20]),
                    'rh': float(row[22]),       # humedad relativa (%) → agua precipitable
                    'pressure': float(row[24]),
                    'dni': float(row[27]),
                    'ghi': float(row[30]),
                    'dhi': float(row[33])
                })
            except (ValueError, IndexError):
                continue
                
    df = pd.DataFrame(data)
    
    # Setear indice de tiempo
    df['time'] = pd.to_datetime(df['time'])
    df.set_index('time', inplace=True)
    
    # Manejar posibles NaNs de la base de datos (marcados como -9999)
    df = df.replace(-9999, np.nan)
    df.dropna(subset=['ghi', 'dni', 'dhi', 'temp_air'], inplace=True)
    
    # Asegurar que el tiempo esté localizado
    if df.index.tz is None:
        df.index = df.index.tz_localize(tz)

    # Red de seguridad ante doble cobertura: el desfase de +6 meses con
    # relativedelta colapsa los días 29-31 de los meses largos sobre el último
    # día de los meses cortos (p. ej. 31-ago → 28-feb), generando timestamps
    # idénticos. Se conserva la primera ocurrencia para no doble-contar.
    n_dup = df.index.duplicated(keep='first').sum()
    if n_dup:
        df = df[~df.index.duplicated(keep='first')]
        print(f"Timestamps duplicados eliminados (red de seguridad): {n_dup}")

    # 3. Limpieza de datos (Quitar valores negativos o faltantes en irradiancia)
    df = df.replace(-9999, np.nan)
    df.dropna(subset=['ghi', 'dni', 'dhi', 'temp_air'], inplace=True)
    df['ghi'] = df['ghi'].clip(lower=0)
    df['dni'] = df['dni'].clip(lower=0)
    df['dhi'] = df['dhi'].clip(lower=0)

    # Humedad relativa y presión para la corrección espectral (rellenar huecos
    # con la mediana para no perder registros eléctricos válidos).
    df['rh'] = df['rh'].clip(lower=0, upper=100)
    df['rh'] = df['rh'].fillna(df['rh'].median())
    df['pressure'] = df['pressure'].fillna(df['pressure'].median())

    # Velocidad de viento asumida (constante, clima desértico suave)
    df['wind_speed'] = 1.0
    
    # 4. Transposición de Irradiancia (POA)
    print("Calculando irradiancia en el Plano del Arreglo (POA)...")
    ALBEDO = 0.20  # suelo desértico genérico (declarado explícitamente, antes default 0.25)
    solar_position = location.get_solarposition(times=df.index)
    dni_extra = pvlib.irradiance.get_extra_radiation(df.index)

    poa_irrad = pvlib.irradiance.get_total_irradiance(
        surface_tilt=tilt,
        surface_azimuth=azimuth,
        dni=df['dni'],
        ghi=df['ghi'],
        dhi=df['dhi'],
        solar_zenith=solar_position['apparent_zenith'],
        solar_azimuth=solar_position['azimuth'],
        dni_extra=dni_extra,
        albedo=ALBEDO,
        model='perez'
    )
    # POA de banda ancha (broadband): mueve la temperatura de celda y es el
    # denominador del PR (irradiancia incidente en el plano, IEC 61724-1).
    df['poa_global'] = poa_irrad['poa_global'].clip(lower=0)

    # ----------------------------------------------------------------------
    # 4b. Irradiancia EFECTIVA: pérdidas ópticas (IAM) + desajuste espectral (AM)
    # ----------------------------------------------------------------------
    # Antes la POA de Perez entraba directa al modelo eléctrico. Ahora se aplican
    # los dos modificadores documentados en el marco teórico (De Soto 2006 §5-7,
    # King 2004): el factor por ángulo de incidencia K_τα(θ) y el factor
    # espectral M(AM, PW). El resultado, poa_effective, es la irradiancia que
    # realmente fotogenera corriente (I_L) en la Fase 4.
    print("Aplicando modificador por ángulo de incidencia (IAM) y corrección espectral (AM)...")

    aoi = pvlib.irradiance.aoi(tilt, azimuth,
                               solar_position['apparent_zenith'],
                               solar_position['azimuth'])

    # IAM directo: modelo físico de Snell-Bouguer (n=1.526 vidrio, K=4 m⁻¹, L=2 mm).
    iam_beam = pvlib.iam.physical(aoi, n=1.526, K=4.0, L=0.002)
    # IAM de la difusa: factores integrados de Marion para cielo y suelo a este tilt.
    iam_dif = pvlib.iam.marion_diffuse('physical', tilt, n=1.526, K=4.0, L=0.002)
    iam_sky, iam_ground = iam_dif['sky'], iam_dif['ground']

    poa_after_iam = (poa_irrad['poa_direct'].clip(lower=0) * iam_beam
                     + poa_irrad['poa_sky_diffuse'].clip(lower=0) * iam_sky
                     + poa_irrad['poa_ground_diffuse'].clip(lower=0) * iam_ground)

    # Factor espectral de First Solar (módulo c-Si ≈ 'monosi' para m-Si y HIT):
    # depende del agua precipitable (humedad+T) y de la masa de aire absoluta.
    pw = pvlib.atmosphere.gueymard94_pw(df['temp_air'], df['rh'])          # cm
    am_rel = pvlib.atmosphere.get_relative_airmass(solar_position['apparent_zenith'])
    am_abs = pvlib.atmosphere.get_absolute_airmass(am_rel, df['pressure'] * 100.0)  # mb→Pa
    spectral_factor = pvlib.spectrum.spectral_factor_firstsolar(pw, am_abs, module_type='monosi')
    spectral_factor = spectral_factor.fillna(1.0).clip(lower=0.8, upper=1.1)

    df['iam_beam'] = iam_beam
    df['spectral_factor'] = spectral_factor
    df['poa_after_iam'] = poa_after_iam.clip(lower=0)
    df['poa_effective'] = (poa_after_iam * spectral_factor).clip(lower=0)

    # Reporte de la magnitud de las nuevas pérdidas (sobre horas de sol).
    sun = df['poa_global'] > 50
    e_glob = df.loc[sun, 'poa_global'].sum()
    e_iam = df.loc[sun, 'poa_after_iam'].sum()
    e_eff = df.loc[sun, 'poa_effective'].sum()
    if e_glob > 0:
        print(f"  Pérdida óptica IAM: {100*(1-e_iam/e_glob):.2f}%  |  "
              f"Pérdida espectral AM: {100*(1-e_eff/e_iam):.2f}%  |  "
              f"Efectiva/Global anual: {100*e_eff/e_glob:.2f}%")

    # 5. Modelo Térmico (Sandia)
    print("Calculando Temperatura de Celda (SAPM)...")
    # Extraemos parámetros empíricos según la tecnología
    if 'mSi' in file_path:
        # Vidrio/Celda/Polímero, rack montado
        temp_model_params = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_polymer']
    else: # HIT
        temp_model_params = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']
        
    df['temp_cell'] = pvlib.temperature.sapm_cell(
        df['poa_global'],
        df['temp_air'],
        df['wind_speed'],
        temp_model_params['a'],
        temp_model_params['b'],
        temp_model_params['deltaT']
    )
    
    # 6. Gráficos y Resultados
    os.makedirs(output_dir, exist_ok=True)
    module_name = 'mSi' if 'mSi' in file_path else 'HIT'
    
    print("Generando Gráficos...")
    # Paso temporal real de la base NREL: una curva I-V cada 5 minutos.
    # La energía se integra como Σ(W/m²)·Δt, con Δt = 5/60 h (antes se omitía
    # el paso, sobreestimando la energía ×12).
    DT_HOURS = 5.0 / 60.0
    # POA Mensual (kWh/m²): potencia media por intervalo × paso temporal.
    poa_monthly = df['poa_global'].resample('ME').sum() * DT_HOURS / 1000  # kWh/m2
    plt.figure(figsize=(10, 5))
    plot_color = '#E8A838' if module_name == 'HIT' else '#007ACC'
    poa_monthly.plot(kind='bar', color=plot_color, edgecolor='white', alpha=0.9)
    plt.title(f'Recurso Solar Mensual POA - {module_name} (Atacama 2026)', fontsize=13, fontweight='bold', pad=15)
    plt.ylabel('Irradiancia (kWh/m2)', fontsize=16)
    plt.xlabel('Mes', fontsize=16)
    plt.xticks(range(12), ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'], rotation=0)
    plt.grid(axis='y', linestyle=':', alpha=0.5)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f'poa_mensual_{module_name}.png'), transparent=True, dpi=150)
    plt.close()
    
    # Histograma Temperatura Celda
    plt.figure(figsize=(10, 7.5))
    hist_color = '#E8A838' if module_name == 'HIT' else '#007ACC'
    df[df['poa_global'] > 10]['temp_cell'].hist(bins=50, color=hist_color, alpha=0.8, edgecolor='none')
    # plt.title(f'Distribución de Temperatura de Celda (Horas de Sol) - {module_name}', fontsize=13, fontweight='bold', pad=15)
    plt.xlabel('Temperatura Celda (°C)', fontsize=16)
    plt.ylabel('Frecuencia', fontsize=16)
    plt.grid(linestyle=':', alpha=0.5)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f'temp_hist_{module_name}.png'), transparent=True, dpi=150, bbox_inches='tight')
    plt.close()
    
    recurso_total = df['poa_global'].sum() * DT_HOURS / 1000
    recurso_efectivo = df['poa_effective'].sum() * DT_HOURS / 1000
    print(f"Recurso Solar Total Anual POA (broadband): {recurso_total:.1f} kWh/m2")
    print(f"Recurso Solar Total Anual POA efectiva (IAM+AM): {recurso_efectivo:.1f} kWh/m2")
    
    # Guardar dataframe limpio para la Fase 2 (Extracción de parámetros)
    print("Guardando datos limpios para Fase 2...")
    
    # Limpiar NAs que resultaron del filtro
    df.dropna(subset=['poa_global', 'temp_cell', 'isc', 'voc'], inplace=True)
    
    out_csv = os.path.join(output_dir, f'Datos_Fase2_{module_name}.csv')
    df.to_csv(out_csv)
    print(f"Listo: {out_csv}\n")

if __name__ == "__main__":
    out_dir = 'output/Fase1_Resultados'
    archivos = ['data/Atacama_2026/Atacama2026_mSi0166.csv', 'data/Atacama_2026/Atacama2026_HIT05667.csv']
    for arch in archivos:
        if os.path.exists(arch):
            procesar_fase1(arch, out_dir)
        else:
            print(f"No se encontró el archivo: {arch}")
