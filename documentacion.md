# os.path.

# .dirname()
Retorna el nombre del directorio de la ruta path.

# os.path.abspath()
Devuelve una versión absoluta normalizada de la ruta de acceso path 

# os.listdir()
Devuelve una lista que contiene los nombres de las entradas en el directorio dado por path. La lista está en un orden arbitrario y no incluye las entradas especiales '.' y '..' incluso si están presentes en el directorio

# .os.path.join()
Une de forma inteligente uno o más segmentos de ruta. El valor devuelto es la concatenación de la ruta y todos los miembros de *paths , con un separador de directorio después de cada parte no vacía, excepto la última. Es decir, el resultado solo terminará en un separador si la última parte está vacía o termina en un separador.

# .os.path.splitext()
Divide el nombre de la ruta path en un par (root, ext) de tal forma que root + ext == path, y ext queda vacío o inicia con un punto y contiene a lo mucho un punto.

Si la ruta no contiene ninguna extensión, ext será ’’.

# python.

# .endswith():
Garantizar que una cadena de texto termine con los caracteres autorizados antes de procesar el flujo.

# librerias.
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

# imagen = ImageReader(ruta_imagen)
Operación: Inicialización del lector de mapas de bits.

Descripción: Abre el archivo de imagen especificado en la ruta de forma binaria. Utiliza internamente los decodificadores de Pillow para interpretar la cabecera del archivo sin cargar la totalidad de los píxeles crudos inmediatamente en memoria.

# ancho, alto = imagen.getSize()
Operación: Extracción de metadatos geométricos.

Descripción: Retorna una tupla de dos enteros (width, height) que representan la resolución espacial pura de la imagen en píxeles.

# pdf = canvas.Canvas(ruta_pdf, pagesize=(ancho, alto))Operación:
 Instanciación del flujo de salida PDF y definición del área de trabajo.

 Descripción: Inicializa el motor de renderizado de ReportLab. Define el tamaño físico de la hoja del documento. En el formato PDF, las unidades por defecto son puntos tipográficos (1/72 de pulgada), pero al igualar píxeles a puntos uno a uno, se genera una traslación directa de coordenadas sin alterar la proporción.
 
# pdf.drawImage(imagen, 0, 0, width=ancho, height=alto)
 Operación: Inyección de matriz gráfica en el lienzo.

 Descripción: Dibuja el flujo de datos de la imagen dentro del archivo PDF en las coordenadas de destino. Al especificar los parámetros width y height de forma idéntica a las dimensiones extraídas en el paso 2, el algoritmo de ReportLab ajusta la caja de visualización (Bounding Box) eliminando cualquier opción de reajuste automático (Letterboxing) o recortes forzados.
 
# pdf.save()
 Operación: Serialización y cierre de flujo de archivos (I/O).

 Descripción: Empaqueta los objetos de la estructura del PDF (páginas, catálogos, flujos de compresión binaria de la imagen), escribe los datos definitivos en el almacenamiento del disco local (ruta_pdf) y libera los descriptores de archivo abiertos para prevenir fugas de memoria en el sistema operativo.