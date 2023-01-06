from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common import exceptions
from selenium.webdriver.chrome.options import Options

from PIL import Image


import time
from . import detection as dt

class Crawler:

  CAPTCHA_PASS = "CAPTCHA Passed."
  CAPTCHA_FAIL = "CAPTCHA Failed"
  NO_RECORD = "No record found."

  def __init__(self, id, self_init = True, headless = True) -> None:
    self.id = id
    self.headless = headless
    options = Options()
    options.add_experimental_option("detach", True)
    options.add_argument("--log-level=3")
    if self.headless:
      options.add_argument("--headless")

    service = Service('chromedriver.exe')
    self.driver = webdriver.Chrome(service=service, chrome_options=options)
    if self_init:
      self.initialize()

  def close(self):
    print(f"Quiting Crawler {self.id}.")
    # self.driver.close()
    self.driver.quit()

  def initialize(self):
    print(f"Initializing Crawler {self.id}.")
    self.driver.get("https://cej.pj.gob.pe/cej/forms/busquedaform.html")
    self.driver.maximize_window()
    
  def home_page(self):
    print(f"Crawler {self.id}: Getting the home page.")
    self.driver.get("https://cej.pj.gob.pe/cej/forms/busquedaform.html")

  def _give_captcha(self):
    print(f"Crawler {self.id}: Getting captcha image.")
    img = Image.open(f"{dt.IMAGES_PATH}/page_{self.id}.png")
    if self.headless:
      img = img.crop((int(img.width/8 - 13), int(img.height/2 + 25), int(img.width/2 - 63), int(img.height*2/3 + 14)))
    else:
      img = img.crop((0,int(img.height/2),int(img.width/2),img.height))  
      img = img.crop((int(img.width*6/13),int(img.height*9/20-110),int(img.width*6/13+300), int(img.height*9/20-2)))
    img.save(f"{dt.IMAGES_PATH}/captcha_{self.id}.png")

  def _solve_captcha(self):
    print(f"Crawler {self.id}: Solving captcha.")
    return dt.run(self.id)
        
  def fill_form(self, district, instance, speciality, year, num, context):
    print(f"Crawler {self.id}: Filling form.")
    driver = self.driver
    
    if context not in [self.NO_RECORD, self.CAPTCHA_FAIL]:
      driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
    driver.find_element(By.CSS_SELECTOR, "img#captcha_image").click()
    time.sleep(2)
    driver.save_screenshot(f"{dt.IMAGES_PATH}/page_{self.id}.png")
    # time.sleep(1)
    self._give_captcha()
    # time.sleep(1)
    captcha = self._solve_captcha()
    
    district_f =  driver.find_element(By.CSS_SELECTOR, "select#distritoJudicial")
    instance_f = driver.find_element(By.CSS_SELECTOR, "select#organoJurisdiccional")
    speciality_f = driver.find_element(By.CSS_SELECTOR, "select#especialidad")
    year_f = driver.find_element(By.CSS_SELECTOR, "select#anio")
    no_f = driver.find_element(By.CSS_SELECTOR, "input#numeroExpediente")
    captcha_f = driver.find_element(By.CSS_SELECTOR, "input#codigoCaptcha")

    driver.implicitly_wait(5)
    Select(district_f).select_by_visible_text(district)
    driver.implicitly_wait(5)
    Select(instance_f).select_by_visible_text(instance)
    driver.implicitly_wait(5)
    Select(speciality_f).select_by_visible_text(speciality)
    driver.implicitly_wait(5)
    Select(year_f).select_by_visible_text(year)
    no_f.clear()
    no_f.send_keys(num)
    # driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")

    try_limit = 3
    i = 0
    while i != try_limit:
      if i != 0:
        driver.find_element(By.CSS_SELECTOR, "img#captcha_image").click()
        time.sleep(2)
        driver.save_screenshot(f"{dt.IMAGES_PATH}/page_{self.id}.png")
        # time.sleep(1)
        self._give_captcha()
        # time.sleep(1)
        captcha = self._solve_captcha()
      captcha_f.send_keys(captcha)
      
      # driver.implicitly_wait(5)
      driver.find_element(By.CSS_SELECTOR, "button#consultarExpedientes").click()

      time.sleep(3)
      try:
        if "none" in driver.find_element(By.CSS_SELECTOR, "span#mensajeNoExisteExpedientes").get_attribute("style"):
          raise exceptions.NoSuchElementException  
        return self.NO_RECORD      
      except exceptions.NoSuchElementException:
        pass

      try: 
        time.sleep(3)
        if "none" in driver.find_element(By.CSS_SELECTOR, "span#codCaptchaError").get_attribute("style"):
          raise exceptions.NoSuchElementException
        driver.find_element(By.CSS_SELECTOR, "img#btnReload").click()
        i+=1
        print(f"Crawler {self.id}: Try {i} failed.")
      except exceptions.NoSuchElementException:
        i = try_limit
        print(f"Crawler {self.id}: Captcha passed.")
        return self.CAPTCHA_PASS
        
    print(f"Crawler {self.id}: Captcha failed.")
    return self.CAPTCHA_FAIL

  def open_file(self, index):
    print(f"Crawler {self.id}: Opening file {index + 1}.")
    driver = self.driver
    driver.implicitly_wait(10)
    records_div = driver.find_element(By.ID, "divDetalles")
    buttons = records_div.find_elements(By.TAG_NAME, "button")
    count = len(buttons)
    buttons[index].click()
    if index < count - 1:
      return False
    else:
      return True
  
  def go_back(self):
    print(f"Crawler {self.id}: Going back.")
    element = self.driver.find_element(By.CSS_SELECTOR, "div#divCuerpo div:nth-child(1) > a:nth-child(1) > img")
    webdriver.ActionChains(self.driver).move_to_element(element).click(element).perform()




if __name__ == "__main__":
  driver = Crawler()
  response = driver.fill_form(driver, "LIMA","JUZGADO ESPECIALIZADO", "CIVIL", "2019", "100")
  print(response)
  if response == driver.CAPTCHA_PASS:
    driver.open_file(driver)
  time.sleep(1000)