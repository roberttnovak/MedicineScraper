import logging
from time import sleep

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver

from medicines import MedicinesSearch

logger = logging.getLogger(__name__)


class Cima:
    _FILTROS_BUSQUEDA = {
        "filtroRecetaSi": "filtro de los medicamentos con receta",
        "filtroRecetaNo": "filtro de los medicamentes sin receta",
        "filtroTrianguloSi": "filtro de los medicamentos con seguimiento adicional",
        "filtroTrianguloNo": "filtro de los medicamentos sin seguimiento adicional",
        "filtroHuerfanoSi": "filtro de los medicamentos que son huérfanos",
        "filtroHuerfanoNo": "filtro de los medicamentos que no son huérfanos",
        "filtroBiosimilarSi": "filtro de los medicamentos que son biosimilares",
        "filtroBiosimilarNo": "filtro de los medicamentos que no son biosimilares",
        "filtroComercializadoSi": "filtro de los medicamentos comercializados",
        "filtroComercializadoNo": "filtro de los medicamentos no comercializados",
        "filtroImpParalelasSi": "filtro de los medicamentos con importación paralela",
        "filtroImpParalelasNo": "filtro de los medicamentos sin importación paralela",
        "filtroAutorizado": "filtro de los medicamentos autorizados",
        "filtroSuspendido": "filtro de los medicamentos suspendidos",
        "filtroRevocado": "filtro de los medicamentos revocados",
        "filtroBiologicos": "filtro de los medicamentos biológicos",
        "filtroPactivos": "filtro de los medicamentos con estrecho margen terapéutico",
        "filtroApRespiratorio": "filtro de los medicamentos por vía respiratoria",
    }

    def __init__(self, driver: webdriver, sleep_time: float, timeout: float) -> None:
        self._driver = driver
        self._sleep_time = sleep_time
        self._timeout = timeout
        self._wait = WebDriverWait(driver, self._timeout)

    def get_home(self):
        self._driver.get("https://cima.aemps.es/cima/publico/home.html")

    def search_medicines(
        self, search: str, search_filters: list, remove_default_filters: bool,
    ) -> MedicinesSearch:
        self.get_home()
        logger.debug(f"Finding {search} ...")
        buscador = self._driver.find_element(By.ID, "inputbuscadorsimple")
        buscador.clear()
        buscador.send_keys(search)
        buscador.send_keys(Keys.ENTER)
        sleep(self._sleep_time)
        self._wait.until(
            EC.presence_of_all_elements_located((By.XPATH, "//*[@id='resultlist']/div"))
        )
        logger.debug(f"Navigated to: '{self._driver.title}'")
        if remove_default_filters:
            self.deselect_all_search_filters()
        if search_filters:
            self.select_search_filters(search_filters)
        num_elements = int(self._driver.find_element(By.ID, "numResultados").text)
        if num_elements == 0:
            raise ValueError("No se ha encontrado ningun resultado para esta búsqueda!")
        logger.info(
            f"Se han encontrado {num_elements} medicamentos para la búsqueda '{search}'"
        )
        return MedicinesSearch(
            self._driver, sleep_time=self._sleep_time, timeout=self._timeout,
        )

    def deselect_all_search_filters(self):
        logger.info("Desactivando todos los filtros activos...")
        for i, v in self._FILTROS_BUSQUEDA.items():
            try:
                # Nos aseguramos de que el código se pueda ejecutar si salta algún error
                if self._driver.find_element(By.ID, i).is_selected():
                    checkbox = self._driver.find_element(
                        By.CSS_SELECTOR, "label[for={}]".format(i)
                    )
                    self._driver.execute_script("arguments[0].click();", checkbox)
            except NoSuchElementException:
                # Identificamos el error correspondiente al de los elementos que identifican los checkbox
                logger.warning(
                    "El {} ya no existe en la página web o su id en el html ha cambiado de nombre".format(
                        v
                    )
                )
            except:
                logger.error("Ha ocurrido un error para el {}".format(v))
                raise
        sleep(self._sleep_time)
        logger.info("Hecho!")

    def select_search_filters(self, filters: list):
        logger.info(f"Activando los siguientes filtros: {' ,'.join(filters)}")
        for i in filters:
            try:
                # Nos aseguramos de que el código se pueda ejecutar si salta algún error
                if not self._driver.find_element(By.ID, i).is_selected():
                    checkbox = self._driver.find_element(
                        By.CSS_SELECTOR, "label[for={}]".format(i)
                    )
                    self._driver.execute_script("arguments[0].click();", checkbox)
            except NoSuchElementException:
                # Identificamos el error correspondiente al de los elementos que identifican los checkbox
                logger.warning(
                    "El {} ya no existe en la página web o su id en el html ha cambiado de nombre".format(
                        self._FILTROS_BUSQUEDA[i]
                    )
                )
            except:
                logger.error(
                    "Ha ocurrido un error para el {}".format(self._FILTROS_BUSQUEDA[i])
                )
                raise
        sleep(self._sleep_time)
        logger.info("Hecho!")
