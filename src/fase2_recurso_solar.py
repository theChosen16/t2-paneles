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
    
    # 3. Limpieza de datos (Quitar valores negativos o faltantes en irradiancia)
    df = df.replace(-9999, np.nan)
    df.dropna(subset=['ghi', 'dni', 'dhi', 'temp_air'], inplace=True)
    df['ghi'] = df['ghi'].clip(lower=0)
    df['dni'] = df['dni'].clip(lower=0)
    df['dhi'] = df['dhi'].clip(lower=0)
    
    # Velocidad de viento asumida (constante, clima desértico suave)
    df['wind_speed'] = 1.0 
    
    # 4. Transposición de Irradiancia (POA)
    print("Calculando irradiancia en el Plano del Arreglo (POA)...")
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
        model='perez'
    )
    df['poa_global'] = poa_irrad['poa_global'].clip(lower=0)
    
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
    # POA Mensual
    poa_monthly = df['poa_global'].resample('ME').sum() / 1000 # kWh/m2
    plt.figure(figsize=(10, 5))
    plot_color = '#E8A838' if module_name == 'HIT' else '#007ACC'
    poa_monthly.plot(kind='bar', color=plot_color, edgecolor='white', alpha=0.9)
    plt.title(f'Recurso Solar Mensual POA - {module_name} (Atacama 2026)', fontsize=13, fontweight='bold', pad=15)
    plt.ylabel('Irradiancia (kWh/m2)', fontsize=11)
    plt.xlabel('Mes', fontsize=11)
    plt.xticks(range(12), ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'], rotation=0)
    plt.grid(axis='y', linestyle=':', alpha=0.5)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f'poa_mensual_{module_name}.png'), transparent=True, dpi=150)
    plt.close()
    
    # Histograma Temperatura Celda
    plt.figure(figsize=(10, 5))
    hist_color = '#E8A838' if module_name == 'HIT' else '#007ACC'
    df[df['poa_global'] > 10]['temp_cell'].hist(bins=50, color=hist_color, alpha=0.8, edgecolor='none')
    plt.title(f'Distribución de Temperatura de Celda (Horas de Sol) - {module_name}', fontsize=13, fontweight='bold', pad=15)
    plt.xlabel('Temperatura Celda (°C)', fontsize=11)
    plt.ylabel('Frecuencia', fontsize=11)
    plt.grid(linestyle=':', alpha=0.5)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f'temp_hist_{module_name}.png'), transparent=True, dpi=150)
    plt.close()
    
    recurso_total = df['poa_global'].sum() / 1000
    print(f"Recurso Solar Total Anual POA: {recurso_total:.2f} kWh/m2")
    
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
