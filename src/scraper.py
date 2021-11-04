import logging

from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
import pandas as pd

from cima import Cima

_DEFAULT_SLEEP_TIME = 3
_DEFAULT_TIMEOUT = 20

logger = logging.getLogger(__name__)


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
    driver = initialize_driver()
    cima_webpage = Cima(driver, _DEFAULT_SLEEP_TIME, _DEFAULT_TIMEOUT)
    medicines_data = cima_webpage.search_medicines(search="*", sleep_time=0.5).scrape_medicines(
        num_medicines=5000
    )
    medicines_table = pd.DataFrame.from_records(
        medicines_data, index="Número de registro"
    )
    out = "medicines_table.csv"
    medicines_table.to_csv(out, index=True)
    logger.info(f"Saved data into {out}")

if __name__ == "__main__":
    logging.basicConfig(
        level="INFO",
        format="%(asctime)s [%(levelname)s] -- %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    main()
