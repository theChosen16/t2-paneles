import pandas as pd
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta

def emular_atacama(input_path, output_path):
    print(f"Procesando {input_path}...")
    
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
                # Sumar 6 meses
                dt = dt + relativedelta(months=6)
                
                # Proyectar a 2026. Manejar si cae 29 feb (dateutil lo maneja automáticamente o podemos forzar)
                if dt.month == 2 and dt.day == 29:
                    dt = dt.replace(year=2026, day=28)
                else:
                    dt = dt.replace(year=2026)
                    
                new_ts = dt.strftime("%Y-%m-%dT%H:%M:%S")
                fout.write(f"{new_ts},{rest}")
            except Exception as e:
                # Si falla (ej data malformada), se deja igual
                fout.write(line)
        
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
