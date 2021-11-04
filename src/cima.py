import logging
from time import sleep

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver

from medicines import MedicinesSearch

logger = logging.getLogger(__name__)


class Cima:
    def __init__(self, driver: webdriver, sleep_time: float, timeout: float) -> None:
        self._driver = driver
        self._sleep_time = sleep_time
        self._timeout = timeout
        self._wait = WebDriverWait(driver, self._timeout)

    def get_home(self):
        self._driver.get("https://cima.aemps.es/cima/publico/home.html")

    def search_medicines(
        self, search: str, sleep_time: float = None, timeout: float = None
    ):
        self.get_home()
        logger.debug(f"Finding {search} ...")
        buscador = self._driver.find_element(By.ID, "inputbuscadorsimple")
        buscador.clear()
        buscador.send_keys(search)
        buscador.send_keys(Keys.ENTER)
        # If we do not wait, the `page_source` will not have time to change and it will be showed the previous page (the homepage in this case)
        sleep(self._sleep_time)
        self._wait.until(
            EC.presence_of_all_elements_located((By.XPATH, "//*[@id='resultlist']/div"))
        )
        logger.debug(f"Navigated to: '{self._driver.title}'")
        num_elements = int(self._driver.find_element(By.ID, "numResultados").text)
        logger.info(f"Found {num_elements} elements for search '{search}'")
        return MedicinesSearch(
            self._driver,
            sleep_time=sleep_time or self._sleep_time,
            timeout=timeout or self._timeout,
        )
