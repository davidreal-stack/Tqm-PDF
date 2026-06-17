from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import os

def encontrar_imagen_en_carpeta():
    # Extensiones de imagen válidas
    extensiones_validas = ('.jpg', '.jpeg', '.png', '.bmp', '.webp')
    
    # Obtener la carpeta actual donde se está ejecutando este script
    carpeta_actual = os.path.dirname(os.path.abspath(__file__))
    
    # Listar todos los archivos y buscar la primera imagen
    for archivo in os.listdir(carpeta_actual):
        if archivo.lower().endswith(extensiones_validas):
            ruta_completa = os.path.join(carpeta_actual, archivo)
            return ruta_completa, archivo
            
    return None, None

def imagen_a_pdf_ajustado():
    # 1. Detectar automáticamente la imagen en la carpeta
    ruta_imagen, nombre_archivo = encontrar_imagen_en_carpeta()
    
    if not ruta_imagen:
        print("❌ Error: No se encontró ninguna imagen (.jpg, .png, etc.) en esta carpeta.")
        print("👉 Por favor, arrastra o copia una imagen dentro de C:\\PROYECTOS\\generador-PDF y vuelve a intentar.")
        return

    print(f"📸 Imagen detectada automáticamente: {nombre_archivo}")

    # 2. Generar el nombre del PDF dinámicamente basado en la imagen
    nombre_base, _ = os.path.splitext(nombre_archivo)
    carpeta_actual = os.path.dirname(ruta_imagen)
    ruta_pdf = os.path.join(carpeta_actual, f"{nombre_base}.pdf")
    
    # 3. Leer las dimensiones reales de la imagen
    imagen = ImageReader(ruta_imagen)
    ancho, alto = imagen.getSize()
    
    # 4. Crear el lienzo del PDF con las medidas exactas
    pdf = canvas.Canvas(ruta_pdf, pagesize=(ancho, alto))
    pdf.drawImage(imagen, 0, 0, width=ancho, height=alto)
    pdf.save()
    
    print(f"✅ PDF creado exitosamente: {nombre_base}.pdf")

# Ejecutar el proceso global
if __name__ == "__main__":
    imagen_a_pdf_ajustado()
