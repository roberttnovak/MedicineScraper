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
        default=False,
        action="store_true",
        help="Activar para mostrar mensajes de debugging (Verbose logging).",
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


def main():
    args = parser_args()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] -- %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    driver = initialize_driver()
    cima_webpage = Cima(driver, args.sleep_time, args.timeout)
    medicines_data = cima_webpage.search_medicines(
        search="*", sleep_time=args.scroll_sleep_time
    ).scrape_medicines(num_medicines=args.num_medicamentos)
    medicines_table = pd.DataFrame.from_records(
        medicines_data, index="Número de registro"
    )
    medicines_table.to_csv(args.out, index=True)
    logger.info(f"Saved data into {args.out}")


if __name__ == "__main__":
    main()
