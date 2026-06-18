import pandas as pd
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta


def _primer_timestamp(input_path):
    """Devuelve el primer timestamp de datos (tras las 2 líneas de metadatos
    y el header) para definir la ventana de 12 meses sin doble cobertura."""
    with open(input_path, 'r', encoding='utf-8') as fin:
        [fin.readline() for _ in range(3)]  # saltar metadatos (2) + header (1)
        for line in fin:
            if not line.strip():
                continue
            ts_str = line.split(',', 1)[0]
            try:
                return datetime.strptime(ts_str, "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                continue
    raise ValueError(f"No se encontró un timestamp válido en {input_path}")


def emular_atacama(input_path, output_path):
    print(f"Procesando {input_path}...")

    # --- Ventana de 12 meses para evitar la DOBLE COBERTURA de meses ---
    # El dataset Cocoa abarca 2011-01-21 → 2012-03-04 (~13.5 meses): la
    # temporada 21-ene → 04-mar aparece DOS veces (2011 y 2012). Sin tratarlo,
    # tras el desfase de +6 meses y forzar el año 2026 esos registros caen en
    # los mismos meses (jul–sep 2026), duplicando timestamps y sesgando la POA
    # mensual y la energía anual (el PR, al ser un cociente, se mantiene).
    # Solución: conservar solo la PRIMERA ventana contigua de 12 meses
    # [t0, t0 + 1 año), de modo que cada mes calendario quede cubierto una
    # sola vez (enero = días 21-31 de 2011 + días 1-20 de 2012, sin solape).
    t0 = _primer_timestamp(input_path)
    corte = t0 + relativedelta(years=1)
    print(f"Ventana de 12 meses: [{t0:%Y-%m-%d} , {corte:%Y-%m-%d}) — "
          f"se descarta la temporada duplicada posterior.")

    n_in = n_out = n_drop_dup = 0
    with open(input_path, 'r', encoding='utf-8') as fin, open(output_path, 'w', encoding='utf-8') as fout:
        # 1. Leer y modificar los metadatos (líneas 1 y 2)
        line1 = fin.readline()
        line2 = fin.readline()

        meta_cols = line1.strip().split(',')
        meta_vals = line2.strip().split(',')

        meta_vals[1] = "San Pedro de Atacama"
        meta_vals[2] = "Antofagasta"
        meta_vals[3] = "-4"
        meta_vals[4] = "-22.91"
        meta_vals[5] = "-68.20"
        meta_vals[6] = "2400.0"
        meta_vals[7] = "22.91"
        meta_vals[8] = "0.0"

        fout.write(line1)
        fout.write(",".join(meta_vals) + "\n")

        # 3. Leer header
        header = fin.readline()
        fout.write(header)

        # 4. Procesar linea a linea
        print("Aplicando desfase estacional y proyectando a 2026...")
        for line in fin:
            if not line.strip(): continue
            parts = line.split(',', 1)
            ts_str = parts[0]
            rest = parts[1] if len(parts) > 1 else ""

            try:
                dt = datetime.strptime(ts_str, "%Y-%m-%dT%H:%M:%S")
                n_in += 1

                # Recorte de doble cobertura: descartar lo que cae fuera de la
                # primera ventana contigua de 12 meses.
                if dt >= corte:
                    n_drop_dup += 1
                    continue

                # Sumar 6 meses
                dt = dt + relativedelta(months=6)

                # Proyectar a 2026. Manejar si cae 29 feb (dateutil lo maneja automáticamente o podemos forzar)
                if dt.month == 2 and dt.day == 29:
                    dt = dt.replace(year=2026, day=28)
                else:
                    dt = dt.replace(year=2026)

                new_ts = dt.strftime("%Y-%m-%dT%H:%M:%S")
                fout.write(f"{new_ts},{rest}")
                n_out += 1
            except Exception as e:
                # Si falla (ej data malformada), se deja igual
                fout.write(line)

    print(f"Filas leídas: {n_in} | escritas: {n_out} | "
          f"descartadas por doble cobertura: {n_drop_dup}")
    print(f"Emulación completada: {output_path}\n")

if __name__ == "__main__":
    # Crear carpeta de salida
    os.makedirs('data/Atacama_2026', exist_ok=True)
    
    # Módulos seleccionados
    modules = ['data/Cocoa/Cocoa_mSi0166.csv', 'data/Cocoa/Cocoa_HIT05667.csv']
    
    for mod in modules:
        if os.path.exists(mod):
            out_name = os.path.join('data/Atacama_2026', os.path.basename(mod).replace('Cocoa', 'Atacama2026'))
            emular_atacama(mod, out_name)
        else:
            print(f"Archivo no encontrado: {mod}")
