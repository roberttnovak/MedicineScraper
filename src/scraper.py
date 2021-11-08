import logging
import argparse

import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver

from cima import Cima

_DEFAULT_SLEEP_TIME = 3
_DEFAULT_SCROLLING_SLEEP_TIME = 0.5
_DEFAULT_TIMEOUT = 20

logger = logging.getLogger(__name__)


def parser_args():

    parser = argparse.ArgumentParser(
        description="Scrape de dataset de medicamentos registrado en el Estado Español."
    )

    parser.add_argument(
        "--search",
        type=str,
        default="*",
        help="Búsqueda por medicamento o principio activo a realizar en la página web.\
            Por defecto estará a '*', de forma que buscará todos los medicamentos disponibles",
    )
    parser.add_argument(
        "--num-medicamentos",
        type=int,
        default=None,
        help="Número de medicamentos a scrapear. Si no se especifica se \
            scrapearan los elementos disponibles en la lista inicial (25).\
            Si se especifica -1 se scraperan todos los medicamentos hasta \
            el final de la lista.",
    )
    parser.add_argument(
        "--out",
        "-o",
        type=str,
        required=True,
        help="Nombre del archivo final (en formato .csv).",
    )
    parser.add_argument(
        "--sleep-time",
        type=float,
        default=_DEFAULT_SLEEP_TIME,
        help="Tiempo de sleep por defecto.",
    )
    parser.add_argument(
        "--scroll-sleep-time",
        type=float,
        default=_DEFAULT_SCROLLING_SLEEP_TIME,
        help="Tiempo de sleep para el scrolling de resultados.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=_DEFAULT_TIMEOUT,
        help="Tiempo de timeout por defecto.",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        help="Activar para mostrar mensajes de debugging (Verbose logging).",
    )
    parser.add_argument(
        "--remove-default-filters",
        action="store_true",
        default=False,
        help="Desactiva todos los filtros de búsqueda por defecto.",
    )

    filters_group = parser.add_argument_group("filtros disponibles")
    for k, v in Cima._FILTROS_BUSQUEDA.items():
        filters_group.add_argument(
            "--" + k,
            action="store_true",
            default=False,
            help="Indica si seleccionar el " + v,
        )

    return parser.parse_args()


def initialize_driver() -> webdriver:
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")  # No interface
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(
        "--user-agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'"
    )
    driver = webdriver.Chrome(
        executable_path=ChromeDriverManager().install(), options=chrome_options
    )
    return driver


def select_items(data: dict, keys_to_select: list):
    items = {}
    for key, value in data.items():
        if key in keys_to_select:
            items[key] = value
    return items


def filterout_false_values(data: dict):
    filtered_data = {}
    for key, value in data.items():
        if value is True:
            filtered_data[key] = value
    return filtered_data


def main():
    args = parser_args()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] -- %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    try:
        driver = initialize_driver()
        cima_webpage = Cima(driver, args.sleep_time, args.timeout)
        search_filters = select_items(
            data=vars(args), keys_to_select=Cima._FILTROS_BUSQUEDA.keys()
        )
        search = cima_webpage.search_medicines(
            search=args.search,
            remove_default_filters=args.remove_default_filters,
            search_filters=list(filterout_false_values(search_filters).keys()),
        )
        medicines_data = search.scrape_medicines(
            num_medicines=args.num_medicamentos,
            scroll_sleep_time=args.scroll_sleep_time,
        )
        medicines_table = pd.DataFrame.from_records(
            medicines_data, index="Número de registro"
        )
        medicines_table.to_csv(args.out, index=True)
        logger.info(f"Datos guardados en {args.out}")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
