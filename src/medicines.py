import re
import logging
from time import sleep
from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException, TimeoutException

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver

logger = logging.getLogger(__name__)


class MedicineDetails:
    def __init__(self, html: str) -> None:
        self._html = html

    def scrape_data(self) -> dict:
        # Utilizamos un objeto BeautifulSoup para scrapear la página
        bs = BeautifulSoup(self._html, "html.parser")

        # A continuación se scrapean todos los elementos presentes en la página:

        # Nombre del medicamento: Está entre identificado por la tag h1
        medicamento = bs.find("h1").get_text()

        # Nombre del laboratorio: Lo identifica la id="nombrelabXS"
        laboratorio = bs.find("div", {"id": "nombrelabXS"}).get_text()

        # Número de registro:  Lo identifica la id="nregistroId"
        num_registro = bs.find("span", {"id": "nregistroId"}).get_text()

        # Comprobamos si un medicamento se ha autorizado o no.
        # Esta información está contenida en la tag h2 identificada por el atributo id=estadoXS
        # Si no está autorizado, entonces la tag esta vacía. Si sí lo está entonces aparece el contenido no vacío con el formato "Autorizado ( dd/mm/aaaa )"
        autorizado_bool = not bs.find("h2", {"id": "estadoXS"}).get_text() == ""
        if autorizado_bool:
            autorizado_fecha = re.sub(
                "\( | \)",  # Quitamos los paréntesis y los espacios
                "",
                re.findall(
                    "\(.*\)",  # Encontramos mediante una expresión regular el contenido de la fecha
                    bs.find("h2", {"id": "estadoXS"}).get_text(),
                )[0],
            ).strip()  # Nos aseguramos de que no hay ningún espacio adicional
        else:
            autorizado_fecha = None

        # Explicación análoga al apartado anterior para, en este caso, el estado de suspendido
        suspendido_bool = not bs.find("h2", {"id": "estadoXSsec"}).get_text() == ""
        if suspendido_bool:
            suspendido_fecha = re.sub(
                "\( | \)",
                "",
                re.findall("\(.*\)", bs.find("h2", {"id": "estadoXSsec"}).get_text())[
                    0
                ],
            ).strip()
        else:
            suspendido_fecha = None

        # Si el medicamento está o no comercializado se identifica con un tag h3 identificado por la id='estadocomercXS'
        comercializado_bool = not bs.find("h3", {"id": "estadocomercXS"}) == None

        # Las siguientes columnas son listas que tienen todas la misma estructura: Una etiqueta div con una id que la identifica.
        # Para extraer la información accedemos a la id correspondiente recorriendo todos los elementos de la lista (del html) y
        # guardándola en una lista (de python)

        vias_administracion = bs.find("div", {"id": "viasadministracion"}).find_all(
            "li"
        )
        vias_administracion = [va.get_text() for va in vias_administracion]

        dosis = bs.find("div", {"id": "dosis"}).find_all("li")
        dosis = [d.get_text() for d in dosis]

        formas_farmaceuticas = bs.find("div", {"id": "formas"}).find_all("li")
        formas_farmaceuticas = [ff.get_text() for ff in formas_farmaceuticas]

        principios_activos = bs.find("div", {"id": "pactivosList"}).find_all("li")
        principios_activos = [pa.get_text() for pa in principios_activos]

        excipientes = bs.find("div", {"id": "excipientesList"}).find_all("li")
        excipientes = [e.get_text() for e in excipientes]

        caracteristicas = bs.find("div", {"id": "caracteristicasList"}).find_all("li")
        caracteristicas = [c.get_text() for c in caracteristicas]

        codigos_atc = bs.find("div", {"id": "atcList"}).find_all("li")
        codigos_atc = [atc.get_text() for atc in codigos_atc]

        # Se guardan todos los elementos extraídos anteriormente en una nueva fila cuyo índice en el DataFrame será el número de registro
        nueva_fila = {
            "Número de registro": num_registro,
            "Medicamento": medicamento,
            "Laboratorio": laboratorio,
            "Autorizado": autorizado_bool,
            "Fecha autorización": autorizado_fecha,
            "Suspendido": suspendido_bool,
            "Fecha suspensión": suspendido_fecha,
            "Comercializado": comercializado_bool,
            "Vías administración": vias_administracion,
            "Dosis": dosis,
            "Formas farmacéuticas": formas_farmaceuticas,
            "Principios activos": principios_activos,
            "Excipientes": excipientes,
            "Características": caracteristicas,
            "Códigos ATC": codigos_atc,
        }

        return nueva_fila


class MedicinesSearch:
    def __init__(self, driver: webdriver, sleep_time: float, timeout: float) -> None:
        self._driver = driver
        self._sleep_time = sleep_time
        self._timeout = timeout
        self._wait = WebDriverWait(driver, self._timeout)

    def scrape_medicines(
        self, num_medicines: int = None, scroll_sleep_time: float = None
    ) -> list:
        data = []
        if not num_medicines:
            # No need of scrolling, only first 25 elements will be scraped
            meds_ids = self.get_medicines_identifiers()
            # Recorremos las ids de todos los medicamentos representado a cada uno por 'm'
            logger.info(f"Retrieved all {len(meds_ids)} medicines identifiers")
            logger.info(
                f"Scraping {len(meds_ids)} medicines by click and back method..."
            )
            for m in meds_ids:
                med_data = self.scrape_medicine_click_and_back(m)
                data.append(med_data)
        else:
            # We have to scroll down the page
            if num_medicines == -1:
                # All medicines available will be scraped
                num_medicines = int(
                    self._driver.find_element(By.ID, "numResultados").text
                )
            logger.info(f"Scraping {num_medicines} medicines by scrolling method...")
            self.scroll_down_until(num_medicines, scroll_sleep_time or self._sleep_time)
            meds_ids = self.get_medicines_identifiers()
            try:
                # Retrieve the numeric part of the identifiers
                meds_id_numbers = []
                for m in meds_ids:
                    num_registro = re.search("\d+", m).group(0)
                    meds_id_numbers.append(num_registro)
                logger.info(f"Retrieved all {len(meds_ids)} medicines identifiers")
                for index, m in enumerate(meds_id_numbers):
                    try:
                        med_data = self.scrape_medicine_by_id_number(m)
                        logger.info(f"Iteración nº {index} - Id medicamento: {m} - Título de página actual: '{self._driver.title}'")
                        data.append(med_data)
                        # Only scrape until reach the defined number of medicines
                        if len(data) >= num_medicines:
                            break
                    except Exception as err:
                        logger.error(
                            f"Iteración nº {index} - Id medicamento: {m} - Título de página actual: '{self._driver.title}'.\n"
                            f"Detalles del error:\n'{err}'"
                        )
                        continue
            except BaseException as err:
                logger.error(f"Un error inesperado ha ocurrido: {err}")
                meds_ids_filename = "meds_ids.txt"
                with open(meds_ids_filename, "w") as out:
                    out.write("\n".join(meds_ids))
                logger.info(
                    f"Saved medicines identifiers into {meds_ids_filename} file."
                )
        logger.info(f"Scraped a total of {len(data)} medicines")
        return data

    def get_medicines_identifiers(self):
        meds = self._driver.find_elements(
            By.CSS_SELECTOR, "div[onclick*=medicamentoOnSelect]"
        )
        meds_ids = []
        for m in meds:
            id = m.get_attribute("onclick")
            meds_ids.append(id)
        return meds_ids

    def scrape_medicine_click_and_back(self, med_id: str):
        # Hacemos click en el elemento de la página web que se identifica por el atributo onclick=i que corresponde al medicamento
        # con el número de registro 'med_id'
        self._driver.find_element(
            By.CSS_SELECTOR, 'div[onclick="{}"]'.format(med_id)
        ).click()

        # Esperamos hasta que se termine de cargar el contenido del html donde se encuentran todos los datos de interés del medicamento
        self._wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "figure")))
        logger.info(f"Navigated to {self._driver.title}.")

        # Accedemos al código fuente de la página una vez que esté se ha terminado de rellenar
        nueva_fila = MedicineDetails(html=self._driver.page_source).scrape_data()

        # Se vuelve atrás esperando a que la página cargue para seguir haciendo el mismo proceso para los demás medicamentos
        self._driver.back()
        self._driver.implicitly_wait(self._timeout)
        logger.info(f"Navigated back to {self._driver.title}.")

        return nueva_fila

    def scrape_medicine_by_id_number(self, med_id_number: int):
        url = "https://cima.aemps.es/cima/publico/detalle.html?nregistro={}".format(
            med_id_number
        )
        self._driver.get(url)
        # Esperamos hasta que se termine de cargar el contenido del html donde se
        # encuentran todos los datos de interés del medicamento
        try:
            # Espera a que cargue el botón de compartir
            self._wait.until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, "button[onclick='compartirMedicamento()'")
                )
            )
        except TimeoutException:
            logger.warning(
                f"El medicamento con id {med_id_number} ha provocado un TimeoutException. "
                 "Se procederá a recargar la página y esperar un tiempo por defecto."
            )
            self._driver.get(url)
            sleep(self._sleep_time)

        # Accedemos al código fuente de la página una vez que esté se ha terminado de rellenar
        nueva_fila = MedicineDetails(html=self._driver.page_source).scrape_data()

        return nueva_fila

    def scroll_down_until(self, max_elements: int, sleep_time: float):
        n_iters = 0
        n_meds = 0
        while n_meds < max_elements:
            n_meds = len(
                self._driver.find_elements(
                    By.CSS_SELECTOR, "div[onclick*=medicamentoOnSelect]"
                )
            )
            # Scroll hasta el final de la página
            self._driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            sleep(sleep_time)
            # Esperar hasta que el último elemento de la lista sea clicable
            self._wait.until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//div[@id='resultlist']/div[last()]//div[contains(@onclick,'medicamentoOnSelect')]",
                    )
                )
            )
            # Por motivos informativos, imprimimos cuantas iteraciones/scrollings llevamos
            n_iters += 1
            if n_meds % 100 == 0:
                logger.info(f"Found {n_meds} elements (in {n_iters} iterations)...")

