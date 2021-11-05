# MedicineScraper
Scraping de dataset de medicamentos registrados por el gobierno de España a partir de la página https://cima.aemps.es/.

## Instalación

Es necesario tener instalado una versión estable de google chrome ya que el scraper utilizará el motor y los drivers de google chrome para su ejecución. No es necesario instalar manualmente los drivers de google chrome, esto se realizará de forma interna si es necesario. 

Las dependencias de python se encuentran en el archivo `requirements.txt` y se puede instalar utilizando el siguiente comando:
```bash
pip install -r requirements.txt
```

## Ejecución

Se puede lanzar una ejecución simple de la siguiente manera:

```bash
python src/scraper.py --out tabla_medicamentos.csv
```

Si se quiere especificar un número determinado de medicamentos:

```bash
python src/scraper.py --num-medicamentos 1000 --out tabla_medicamentos.csv
```

## Lista completa de parámetros
```bash
usage: scraper.py [-h] [--num-medicamentos NUM_MEDICAMENTOS] --out OUT [--sleep-time SLEEP_TIME] [--scroll-sleep-time SCROLL_SLEEP_TIME] [--timeout TIMEOUT] [-v]

Scrape de dataset de medicamentos registrado en el Estado Español.

optional arguments:
  -h, --help            show this help message and exit
  --num-medicamentos NUM_MEDICAMENTOS
                        Número de medicamentos a scrapear. Si no se especifica se scrapearan los elementos disponibles en la lista inicial (25). Si se especifica -1 se
                        scraperan todos los medicamentos hasta el final de la lista.
  --out OUT, -o OUT     Nombre del archivo final (en formato .csv).
  --sleep-time SLEEP_TIME
                        Tiempo de sleep por defecto.
  --scroll-sleep-time SCROLL_SLEEP_TIME
                        Tiempo de sleep para el scrolling de resultados.
  --timeout TIMEOUT     Tiempo de timeout por defecto.
  -v, --verbose         Activar para mostrar mensajes de debugging (Verbose logging).
```

Se puede consultar este listado en cualquier momento utilizando el siguiente comando:
```bash
python src/scraper.py --help
```