# -*- coding: utf-8 -*-
"""
FASE 8 — Simulación con RECURSO METEOROLÓGICO REAL de Atacama (PVGIS TMY).

Motivación
----------
El track principal (Fases 1-4) emula Atacama desplazando estacionalmente los
datos medidos del NREL en Cocoa, Florida. Eso valida el modelo ELÉCTRICO con
mediciones reales, pero conserva las MAGNITUDES de irradiancia/temperatura de
Florida (POA ≈ 1,2 MWh/m²·año). Esta fase AÑADE —sin reemplazar nada— un
segundo track alimentado con el recurso solar REAL de San Pedro de Atacama,
para entregar energía y economía con valores absolutos representativos.

Fuente de datos
---------------
PVGIS (Photovoltaic Geographical Information System), Joint Research Centre de
la Comisión Europea — base SARAH (satelital). Año Meteorológico Típico (TMY)
horario para (lat −22.91°, lon −68.20°), descargado con
`pvlib.iotools.get_pvgis_tmy` (sin clave de API) y cacheado en
`data/Atacama_TMY/`. GHI anual ≈ 2.596 kWh/m²·año (recurso desértico real).

Metodología (idéntica al track emulado)
---------------------------------------
Perez (POA, albedo 0.20) → IAM físico + factor espectral First Solar →
Tc Sandia (SAPM, viento real del TMY) → De Soto con los 5 parámetros
extraídos de las mediciones NREL (Fase 3) → PR, energía y yield (paso 1 h).

Salida: temp/resultados_atacama_real.json y gráficos comparativos.
"""
import os
import sys
import json
import numpy as np
import pandas as pd
import pvlib

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

LAT, LON, ELEV = -22.91, -68.20, 2400.0
TILT, AZIMUTH = 22.91, 0.0          # azimut 0° = Norte (hemisferio sur)
TZ = 'Etc/GMT+4'
ALBEDO = 0.20
DT_HOURS = 1.0                       # TMY PVGIS: cadencia horaria
PRECIO_USD_MWH = 45.0
PLANTA_MWP = 100.0
CACHE = 'data/Atacama_TMY/pvgis_tmy_sanpedro.csv'


def cargar_tmy():
    """Descarga (o carga del caché) el TMY horario de PVGIS para San Pedro."""
    if os.path.exists(CACHE):
        print(f"Cargando TMY cacheado: {CACHE}")
        df = pd.read_csv(CACHE, index_col=0, parse_dates=True)
        if df.index.tz is None:
            df.index = df.index.tz_localize('UTC')
        return df
    print("Descargando TMY de PVGIS (JRC, Comisión Europea)...")
    data, meta = pvlib.iotools.get_pvgis_tmy(LAT, LON, map_variables=True)
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    data.to_csv(CACHE)
    print(f"TMY guardado en caché: {CACHE}")
    return data


def recurso_efectivo(df):
    """POA (Perez) + IAM + corrección espectral, idéntico a la Fase 2."""
    loc = pvlib.location.Location(LAT, LON, TZ, ELEV, 'San Pedro de Atacama')
    solpos = loc.get_solarposition(df.index)
    dni_extra = pvlib.irradiance.get_extra_radiation(df.index)

    poa = pvlib.irradiance.get_total_irradiance(
        surface_tilt=TILT, surface_azimuth=AZIMUTH,
        dni=df['dni'], ghi=df['ghi'], dhi=df['dhi'],
        solar_zenith=solpos['apparent_zenith'], solar_azimuth=solpos['azimuth'],
        dni_extra=dni_extra, albedo=ALBEDO, model='perez')
    poa_global = poa['poa_global'].clip(lower=0)

    aoi = pvlib.irradiance.aoi(TILT, AZIMUTH, solpos['apparent_zenith'], solpos['azimuth'])
    iam_beam = pvlib.iam.physical(aoi, n=1.526, K=4.0, L=0.002)
    iam_dif = pvlib.iam.marion_diffuse('physical', TILT, n=1.526, K=4.0, L=0.002)
    poa_iam = (poa['poa_direct'].clip(lower=0) * iam_beam
               + poa['poa_sky_diffuse'].clip(lower=0) * iam_dif['sky']
               + poa['poa_ground_diffuse'].clip(lower=0) * iam_dif['ground'])

    pw = pvlib.atmosphere.gueymard94_pw(df['temp_air'], df['relative_humidity'])
    am_rel = pvlib.atmosphere.get_relative_airmass(solpos['apparent_zenith'])
    am_abs = pvlib.atmosphere.get_absolute_airmass(am_rel, df['pressure'])
    M = pvlib.spectrum.spectral_factor_firstsolar(pw, am_abs, module_type='monosi')
    M = M.fillna(1.0).clip(lower=0.8, upper=1.1)

    poa_eff = (poa_iam * M).clip(lower=0)
    return solpos, poa_global, poa_eff


def simular(module_name, params, df, poa_global, poa_eff):
    # Temperatura de celda según el encapsulado, con viento REAL del TMY.
    if module_name == 'mSi':
        tparams = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_polymer']
    else:
        tparams = pvlib.temperature.TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']
    temp_cell = pvlib.temperature.sapm_cell(
        poa_global, df['temp_air'], df['wind_speed'].clip(lower=0),
        tparams['a'], tparams['b'], tparams['deltaT'])

    IL, Io, Rs, Rsh, a = pvlib.pvsystem.calcparams_desoto(
        poa_eff, temp_cell, alpha_sc=params['alpha_isc'], a_ref=params['a_ref'],
        I_L_ref=params['IL_ref'], I_o_ref=params['Io_ref'], R_sh_ref=params['Rsh_ref'],
        R_s=params['Rs_ref'], EgRef=1.121, dEgdT=-0.0002677)
    pmp = pvlib.pvsystem.singlediode(IL, Io, Rs, Rsh, a)['p_mp']

    ILs, Ios, Rss, Rshs, as_ = pvlib.pvsystem.calcparams_desoto(
        1000, 25, alpha_sc=params['alpha_isc'], a_ref=params['a_ref'],
        I_L_ref=params['IL_ref'], I_o_ref=params['Io_ref'], R_sh_ref=params['Rsh_ref'],
        R_s=params['Rs_ref'])
    p_stc = float(pvlib.pvsystem.singlediode(ILs, Ios, Rss, Rshs, as_)['p_mp'])

    p_ideal = (poa_global / 1000.0) * p_stc
    pr = float(pmp.sum() / p_ideal.sum())
    energia = float(pmp.sum() * DT_HOURS / 1000.0)            # kWh/panel·año
    yield_esp = energia / (p_stc / 1000.0)                    # kWh/kWp·año
    tc_max = float(temp_cell.max())
    return {'pr': pr, 'p_stc': p_stc, 'energia_dc': energia, 'yield': yield_esp,
            'tc_max': tc_max, 'pmp': pmp, 'temp_cell': temp_cell}


def main():
    df = cargar_tmy()
    poa_anual = float(df['ghi'].sum() * DT_HOURS / 1000.0)
    print(f"Recurso del sitio (PVGIS TMY): GHI anual ≈ {poa_anual:.0f} kWh/m²·año")

    with open('temp/parametros_desoto.json', 'r') as f:
        all_params = json.load(f)

    solpos, poa_global, poa_eff = recurso_efectivo(df)
    poa_glob_anual = float(poa_global.sum() * DT_HOURS / 1000.0)
    poa_eff_anual = float(poa_eff.sum() * DT_HOURS / 1000.0)
    print(f"POA en plano (Perez, albedo {ALBEDO}): {poa_glob_anual:.0f} kWh/m²·año | "
          f"efectiva (IAM+AM): {poa_eff_anual:.0f} kWh/m²·año")

    res = {'fuente': 'PVGIS TMY (JRC, base SARAH) — San Pedro de Atacama',
           'ghi_anual_kwh_m2': round(poa_anual, 0),
           'poa_global_anual_kwh_m2': round(poa_glob_anual, 0),
           'poa_efectiva_anual_kwh_m2': round(poa_eff_anual, 0),
           'modulos': {}}
    sims = {}
    for mod in ['mSi', 'HIT']:
        s = simular(mod, all_params[mod], df, poa_global, poa_eff)
        sims[mod] = s
        print(f"  {mod}: PR={s['pr']*100:.2f}% | yield={s['yield']:.0f} kWh/kWp | "
              f"E={s['energia_dc']:.0f} kWh/panel | Tc_max={s['tc_max']:.1f}°C")
        res['modulos'][mod] = {k: round(v, 4) for k, v in s.items()
                               if k in ('pr', 'p_stc', 'energia_dc', 'yield', 'tc_max')}

    # Economía con recurso real (planta 100 MWp, comparación a igual potencia nominal).
    d_yield = sims['HIT']['yield'] - sims['mSi']['yield']           # kWh/kWp·año
    d_energia_mwh = d_yield * (PLANTA_MWP * 1000.0) / 1000.0        # MWh/año en 100 MWp
    d_usd = d_energia_mwh * PRECIO_USD_MWH
    res['economia_100MWp'] = {
        'delta_yield_kwh_kwp': round(d_yield, 1),
        'delta_energia_mwh_anual': round(d_energia_mwh, 0),
        'delta_usd_anual': round(d_usd, 0),
        'precio_usd_mwh': PRECIO_USD_MWH}
    res['delta_pr_puntos'] = round((sims['HIT']['pr'] - sims['mSi']['pr']) * 100, 2)
    print(f"  ΔPR = {res['delta_pr_puntos']} pts | "
          f"Δyield = {d_yield:.0f} kWh/kWp → +{d_energia_mwh:.0f} MWh/año → "
          f"+USD {d_usd:,.0f}/año en {PLANTA_MWP:.0f} MWp")

    os.makedirs('temp', exist_ok=True)
    with open('temp/resultados_atacama_real.json', 'w', encoding='utf-8') as f:
        json.dump(res, f, indent=2, ensure_ascii=False)
    print("\nResultados guardados en temp/resultados_atacama_real.json")
    _graficos(df, poa_global, sims)
    return res


def _graficos(df, poa_global, sims):
    import matplotlib.pyplot as plt
    plt.style.use('dark_background')
    plt.rcParams.update({'figure.facecolor': 'none', 'axes.facecolor': 'none',
                         'savefig.facecolor': 'none', 'text.color': '#FFFFFF',
                         'axes.labelcolor': '#FFFFFF', 'xtick.color': '#CCCCCC',
                         'ytick.color': '#CCCCCC', 'grid.color': '#44445c'})
    out = 'output/Extra_Resultados'
    os.makedirs(out, exist_ok=True)

    # PR mensual real por tecnología.
    fig, ax = plt.subplots(figsize=(11, 5.2))
    for mod, color in [('mSi', '#007ACC'), ('HIT', '#E8A838')]:
        pmp = sims[mod]['pmp']
        p_ideal = (poa_global / 1000.0) * sims[mod]['p_stc']
        pr_m = pmp.resample('ME').sum() / p_ideal.resample('ME').sum()
        ax.plot(range(1, 13), pr_m.values, marker='o', lw=3, ms=8,
                color=color, label=f'PR {"m-Si" if mod=="mSi" else "HIT"}')
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'])
    ax.set_ylabel('Performance Ratio'); ax.set_xlabel('Mes')
    ax.set_title('PR mensual con recurso REAL de Atacama (PVGIS TMY)', fontweight='bold', pad=12)
    ax.grid(True, ls=':', alpha=0.5); ax.legend(fontsize=11)
    fig.tight_layout()
    fig.savefig(os.path.join(out, 'pr_mensual_atacama_real.png'), transparent=True, dpi=150)
    plt.close(fig)

    # Comparación de yield: emulado (Florida) vs real (Atacama).
    try:
        with open('output/Fase2_Resultados/Simulacion_mSi_Atacama.csv') as _:
            pass
    except Exception:
        pass
    fig, ax = plt.subplots(figsize=(9, 5.2))
    labels = ['m-Si', 'HIT']
    yreal = [sims['mSi']['yield'], sims['HIT']['yield']]
    x = np.arange(len(labels)); w = 0.6
    bars = ax.bar(x, yreal, w, color=['#007ACC', '#E8A838'], edgecolor='white', alpha=0.9)
    for b, v in zip(bars, yreal):
        ax.text(b.get_x() + b.get_width()/2, v + 20, f'{v:.0f}', ha='center',
                fontsize=14, fontweight='bold', color='#FFFFFF')
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=13)
    ax.set_ylabel('Yield específico (kWh/kWp·año)')
    ax.set_title('Yield con recurso REAL de Atacama (PVGIS TMY)', fontweight='bold', pad=12)
    ax.grid(True, axis='y', ls=':', alpha=0.5)
    fig.tight_layout()
    fig.savefig(os.path.join(out, 'yield_atacama_real.png'), transparent=True, dpi=150)
    plt.close(fig)
    print("Gráficos del recurso real guardados en output/Extra_Resultados/")


if __name__ == '__main__':
    main()
