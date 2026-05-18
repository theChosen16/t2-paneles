import os
import sys
import win32com.client

def export_pptx_to_png(pptx_path, output_dir):
    # Asegurar rutas absolutas
    pptx_path = os.path.abspath(pptx_path)
    output_dir = os.path.abspath(output_dir)
    
    if not os.path.exists(pptx_path):
        print(f"Error: {pptx_path} no existe.")
        sys.exit(1)
        
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    print(f"Abriendo PowerPoint para exportar {pptx_path}...")
    
    # Iniciar PowerPoint
    powerpoint = win32com.client.Dispatch("PowerPoint.Application")
    
    try:
        # Abrir la presentación
        presentation = powerpoint.Presentations.Open(pptx_path, WithWindow=False)
        
        # Exportar cada slide como PNG
        total_slides = presentation.Slides.Count
        print(f"Exportando {total_slides} diapositivas a {output_dir}...")
        
        for idx in range(1, total_slides + 1):
            slide = presentation.Slides(idx)
            slide_path = os.path.join(output_dir, f"slide_{idx}.png")
            # Exportar (usar formato PNG)
            slide.Export(slide_path, "PNG")
            print(f"  Slide {idx}/{total_slides} exportado a {slide_path}")
            
        presentation.Close()
        print("Exportación completada con éxito.")
    except Exception as e:
        print(f"Error durante la exportación: {e}")
    finally:
        powerpoint.Quit()

if __name__ == "__main__":
    pptx_path = "output/Presentacion_Final_ELI556_Atacama.pptx"
    output_dir = "output/slide_preview"
    export_pptx_to_png(pptx_path, output_dir)
