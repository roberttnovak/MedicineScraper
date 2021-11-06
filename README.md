# MedicineScraper
Scraping de dataset de medicamentos registrados por el gobierno de España a partir de la página https://cima.aemps.es/.

## Instalación

Es necesario tener instalado una versión estable de google chrome ya que el scraper utilizará el motor y los drivers de google chrome para su ejecución. No es necesario instalar manualmente los drivers de google chrome, esto se realizará de forma interna (si es necesario). 

Las dependencias de python se encuentran en el archivo `requirements.txt` y se puede instalar utilizando el siguiente comando:
```bash
pip install -r requirements.txt
```

## Ejecución

Se puede lanzar una búsqueda simple de la siguiente manera:

```bash
python src/scraper.py --search "paracetamol" --out tabla_medicamentos.csv
```

Para obtener un número determinado de medicamentos:

```bash
python src/scraper.py --num-medicamentos 1000 --out tabla_medicamentos.csv
```

## Lista completa de parámetros
```bash
usage: scraper.py [-h] [--search SEARCH] [--num-medicamentos NUM_MEDICAMENTOS] --out OUT [--sleep-time SLEEP_TIME]
                  [--scroll-sleep-time SCROLL_SLEEP_TIME] [--timeout TIMEOUT] [-v] [--remove-default-filters]
                  [--filtroRecetaSi] [--filtroRecetaNo] [--filtroTrianguloSi] [--filtroTrianguloNo] [--filtroHuerfanoSi]
                  [--filtroHuerfanoNo] [--filtroBiosimilarSi] [--filtroBiosimilarNo] [--filtroComercializadoSi]
                  [--filtroComercializadoNo] [--filtroImpParalelasSi] [--filtroImpParalelasNo] [--filtroAutorizado]
                  [--filtroSuspendido] [--filtroRevocado] [--filtroBiologicos] [--filtroPactivos] [--filtroApRespiratorio]

Scrape de dataset de medicamentos registrado en el Estado Español.

optional arguments:
  -h, --help            show this help message and exit
  --search SEARCH       Búsqueda por medicamento o principio activo a realizar en la página web. Por defecto estará a '*',
                        de forma que buscará todos los medicamentos disponibles
  --num-medicamentos NUM_MEDICAMENTOS
                        Número de medicamentos a scrapear. Si no se especifica se scrapearan los elementos disponibles en
                        la lista inicial (25). Si se especifica -1 se scraperan todos los medicamentos hasta el final de
                        la lista.
  --out OUT, -o OUT     Nombre del archivo final (en formato .csv).
  --sleep-time SLEEP_TIME
                        Tiempo de sleep por defecto.
  --scroll-sleep-time SCROLL_SLEEP_TIME
                        Tiempo de sleep para el scrolling de resultados.
  --timeout TIMEOUT     Tiempo de timeout por defecto.
  -v, --verbose         Activar para mostrar mensajes de debugging (Verbose logging).
  --remove-default-filters
                        Desactiva todos los filtros de búsqueda por defecto.

Filtros disponibles:
  --filtroRecetaSi      Indica si seleccionar el filtro de los medicamentos con receta
  --filtroRecetaNo      Indica si seleccionar el filtro de los medicamentes sin receta
  --filtroTrianguloSi   Indica si seleccionar el filtro de los medicamentos con seguimiento adicional
  --filtroTrianguloNo   Indica si seleccionar el filtro de los medicamentos sin seguimiento adicional
  --filtroHuerfanoSi    Indica si seleccionar el filtro de los medicamentos que son huérfanos
  --filtroHuerfanoNo    Indica si seleccionar el filtro de los medicamentos que no son huérfanos
  --filtroBiosimilarSi  Indica si seleccionar el filtro de los medicamentos que son biosimilares
  --filtroBiosimilarNo  Indica si seleccionar el filtro de los medicamentos que no son biosimilares
  --filtroComercializadoSi
                        Indica si seleccionar el filtro de los medicamentos comercializados
  --filtroComercializadoNo
                        Indica si seleccionar el filtro de los medicamentos no comercializados
  --filtroImpParalelasSi
                        Indica si seleccionar el filtro de los medicamentos con importación paralela
  --filtroImpParalelasNo
                        Indica si seleccionar el filtro de los medicamentos sin importación paralela
  --filtroAutorizado    Indica si seleccionar el filtro de los medicamentos autorizados
  --filtroSuspendido    Indica si seleccionar el filtro de los medicamentos suspendidos
  --filtroRevocado      Indica si seleccionar el filtro de los medicamentos revocados
  --filtroBiologicos    Indica si seleccionar el filtro de los medicamentos biológicos
  --filtroPactivos      Indica si seleccionar el filtro de los medicamentos con estrecho margen terapéutico
  --filtroApRespiratorio
                        Indica si seleccionar el filtro de los medicamentos por vía respiratoria
```

Se puede consultar este listado en cualquier momento utilizando el siguiente comando:
```bash
python src/scraper.py --help
```