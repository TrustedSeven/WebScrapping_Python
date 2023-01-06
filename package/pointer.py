from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

class Pointer:

  FOUND = "found"
  NOT_FOUND = "not_found"

  def __init__(self, driver: webdriver.Chrome) -> None:
    self.driver = driver
    self.pointers = self._find_pointers()

  def _find_next_button(self, pointers: list[WebElement]):
    for pointer in pointers:
      if ">" in pointer.text:
        return pointer
    return None

  def _find_pointers(self):
    pointer_div = self.driver.find_element(By.ID, "paginacion1")
    return pointer_div.find_elements(By.TAG_NAME, "li")

  def next_page(self):
    button = self._find_next_button(self.pointers)
    if button == None:
      return self.NOT_FOUND
    else:
      button.find_element(By.TAG_NAME, "a").click()
      self.pointers = self._find_pointers()
      return self.FOUND


  