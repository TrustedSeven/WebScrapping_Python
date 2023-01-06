from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common import exceptions

from . import pointer as pt

class Scraper:
   
  def __init__(self, driver: webdriver.Chrome, id) -> None:
    self.driver = driver
    self.id = id

  def scrape_records_page(self):
    print(f"Scraper {self.id}: Scraping records page.")
    records_div_texts = self.driver.find_element(By.ID, "divDetalles").text.split("\n")
    demandas = []

    for i in range(len(records_div_texts)):
      text = records_div_texts[i]
      if "DEMANDANTE" in text or "DEMANDADO" in text:
        semi_texts = text.split(":")
        try:
          demandas.append((semi_texts[1].replace(". DEMANDADO", "."), semi_texts[2]))
        except:
          demandas.append((semi_texts[1].replace(". DEMANDADO", "."), "N/A"))
    return demandas


  def get_main_info(self):
    print(f"Crawler {self.id}: Getting main info.")
    driver = self.driver
    driver.implicitly_wait(10)

    # demandante = []
    # demandado = []
    # body_texts = driver.find_element(By.TAG_NAME, "body").text
    # for i in range(len(body_texts)):
    #   text = body_texts[i]
    #   if text == "DEMANDANTE":
    #     demandante.append(body_texts[i+2])
    #   elif text == "DEMANDADO":
    #     demandado.append(body_texts[i+2])
    # demandante = ";".join(demandante)
    # demandado = ";".join(demandado)

    numero = driver.find_element(By.CSS_SELECTOR, "div#gridRE b").text
    district = driver.find_element(By.CSS_SELECTOR, "div#gridRE div:nth-child(2) > div:nth-child(4)").text
    instance = driver.find_element(By.CSS_SELECTOR, "div#gridRE div:nth-child(2) > div:nth-child(2)").text
    speciality = driver.find_element(By.CSS_SELECTOR, "div#gridRE div:nth-child(5) > div:nth-child(4)").text
    date = driver.find_element(By.CSS_SELECTOR, "div#gridRE div:nth-child(4) > div:nth-child(2)").text
    year = numero.split("-")[1]
    n_expediente = numero.split("-")[0]
    materia = driver.find_element(By.CSS_SELECTOR, "div#gridRE div:nth-child(6) > div:nth-child(2)").text
    estado = driver.find_element(By.CSS_SELECTOR, "div#gridRE div:nth-child(6) > div:nth-child(4)").text

    main_fields = [
      numero, 
      district, 
      instance, 
      speciality, 
      date, 
      int(year), 
      n_expediente,
      materia,
      estado,
      # demandante,
      # demandado,
      ]

    return main_fields

  def get_follow_ups(self):
    print(f"Crawler {self.id}: Getting follow-ups.")
    driver = self.driver
    i = 0
    follow_ups = []
    pointer = pt.Pointer(driver)
    while True:
      i+=1
      # follow_up = []
      
      try:
        texts = driver.find_element(By.ID, f"pnlSeguimiento{i}").text.split("\n")
        if len(texts) == 1:
          result = pointer.next_page()
          if result == pointer.NOT_FOUND:
            break
          elif result == pointer.FOUND:
            texts = driver.find_element(By.ID, f"pnlSeguimiento{i}").text.split("\n")
            if len(texts) == 1:
              break

        prov_ind = texts.index("Proveido:")
        sum_ind = texts.index("Sumilla:")
        follow_ups.append(texts[prov_ind+1])
        follow_ups.append(texts[sum_ind+1])

      except exceptions.NoSuchElementException:
        break
      except ValueError:
        follow_ups.append([f"value error @ {i}"])

    return follow_ups


if __name__ == "__main__":
  pass
  # driver = crawler.initialize()
  # response = crawler.fill_form(driver, "LIMA","JUZGADO ESPECIALIZADO", "CIVIL", "2019", "100")
  # # response = crawler.fill_form(driver, "LIMA","JUZGADO ESPECIALIZADO", "COMERCIAL", "2021", "8484")
  # print(response)
  # if response == crawler.CAPTCHA_PASS:
  #   crawler.open_file(driver)
  # #main_fields = get_main_info()
  # #follow_ups = get_follow_ups()
  # # print(follow_ups)
  # # print(len(follow_ups))
  # crawler.time.sleep(1000)



