import pandas as pd
import pvlib

def buscar_modulos():
    print("Obteniendo bases de datos de módulos de pvlib...")
    try:
        # Base de datos CEC (California Energy Commission)
        cec_modules = pvlib.pvsystem.retrieve_sam('cecmod')
        
        # Base de datos Sandia
        sandia_modules = pvlib.pvsystem.retrieve_sam('sandiamod')
        
        print(f"\nMódulos en base CEC: {len(cec_modules.columns)}")
        print(f"Módulos en base Sandia: {len(sandia_modules.columns)}")
        
        # Nombres que buscamos de Cocoa
        criterios = ['mSi', 'HIT', 'CdTe', 'CIGS', '0166', '05667', '39017', '75638']
        
        for base_name, base_data in [("CEC", cec_modules), ("Sandia", sandia_modules)]:
            print(f"\n--- Búsqueda en base {base_name} ---")
            for criterio in criterios:
                # Buscamos coincidencias (case insensitive)
                matches = [m for m in base_data.columns if criterio.lower() in m.lower()]
                if matches:
                    print(f"Encontrado '{criterio}': {len(matches)} coincidencias. Ejemplos: {matches[:3]}")
                
    except Exception as e:
        print(f"Error al obtener bases de datos: {e}")

if __name__ == "__main__":
    buscar_modulos()
