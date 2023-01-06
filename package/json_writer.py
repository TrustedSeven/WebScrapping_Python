from . import detection as dt
# import detection as dt

import os
import json

class JsonWriter:
  JSONS_PATH = os.path.join(dt.PROJECT_BASE, "jsons")
  DISTRICT = "district"
  INSTANCE = "instance"
  SPECIALITY = "speciality"
  YEAR = "year"
  STARTING_FILE_NO = "starting_file_no"
  ENDING_FILE_NO = "ending_file_no"
  EXCEL_FILE_NAME = "excel_file_name"
  OVERWRITE = "overwrite"
  FILES = "files"
  BOTS = "bots"
  ID = "id"
  DONE_FILES = "done_files"
  CAPTCHA_FAILED = "captcha_failed"
  DATA = "data"
  COMPLETED = "completed"
  META = "meta.json"

  file_name = None

  def __init__(self, project_name: str) -> None:
    self.project_name = project_name
    self.project_path = os.path.join(self.JSONS_PATH, self.project_name)

  def file_path(self, file_name):
    return os.path.join(self.project_path, file_name)

  def change_field(self, name: str, value):
    with open(self.file_path(self.file_name), "r") as file:
      _json = json.load(file)
    with open(self.file_path(self.file_name), "w") as file:
      _json[name] = value
      json.dump(_json, file)

  def read(self, field: str = None, entire_file: bool = True, name: str = None):
    if name == None:
      name = self.file_name
    with open(self.file_path(name), "r") as file:
      if entire_file:
        return json.load(file)
      else:
        return json.load(file)[field]

  def get_all_subprocess_data(self):
    data = []
    count = len(os.listdir(self.project_path)) - 1
    for i in range(count):
      d = self.read(name=f"{i+1}.json", field=self.DATA, entire_file=False)
      data.extend(d)
    return data

  def create(self, data: dict, name: str = file_name):
    with open(self.file_path(name), "w") as file:
      json.dump(data, file)

if __name__ == "__main__":
  import time
  import numpy as np

  def generate_bots(files: list = None):
    bots = [  ]
    cores = os.cpu_count()

    if len(files) < cores:
      count = 1
    else:
      count = cores


    split_files = np.array_split(files, count)
    for i in range(count):
      bot = {
        "id" : i + 1,
        "files" : [int(x) for x in split_files[i]],
      }

      bots.append(bot)

    return bots



  print()
  print("PROYECTO DE WEB SCRAPING")
  print("========================")
  print()
  print("Website: https://cej.pj.gob.pe/cej/forms/busquedaform.html")
  print()
  old_or_new = input("Do you wish to run a previously incomplete session or a completely new session? (old/new) ").lower()
  if old_or_new[0] == "o":
    incomplete = os.listdir(JsonWriter.JSONS_PATH)
    if len(incomplete) == 0:
      print("No incomplete projects found.")
    else:
      for p in incomplete:
        print()
        jw = JsonWriter(p)
        print(f"Project name: {p}")
        jw.file_name = jw.META
        info = jw.read()
        for key, val in info.items():
          print(f"{key}: {val}")
      print()
      project_name = input("Enter project name: ")
      jw = JsonWriter(project_name)
      jw.file_name = jw.META
      meta_data = jw.read()
      district = meta_data[jw.DISTRICT]
      instance = meta_data[jw.INSTANCE]
      speciality = meta_data[jw.SPECIALITY]
      year = meta_data[jw.YEAR]
      starting_file_no = meta_data[jw.STARTING_FILE_NO]
      ending_file_no = meta_data[jw.ENDING_FILE_NO]
      excel_file_name = meta_data[jw.EXCEL_FILE_NAME]
      overwrite = meta_data[jw.OVERWRITE]
      files = meta_data[jw.FILES]
      bots = meta_data[jw.BOTS]

  else:
    district = input("Ingresar 'Distrito Judicial': ").upper()
    instance = input("Ingresar 'Instancia': ").upper()
    speciality = input("Ingresar 'Especialidad': ").upper()
    year = input("Ingresar 'Año': ").upper()
    starting_file_no = int(input("N° Expediente inicial: "))
    ending_file_no = int(input("N° Expediente final: "))
    project_name = input("Nombre de Proyecto: ")
    excel_file_name = project_name + ".xlsx"
    overwrite = input("Overwrite the excel file or append to it? ").lower()
    if overwrite[0] == "o":
      overwrite = True
    else:
      overwrite = False

    print()
    print()
    print()
    print()

    files = list(range(starting_file_no, ending_file_no + 1))
    bots = generate_bots(files)
    jw = JsonWriter(project_name)
    os.mkdir(os.path.join(JsonWriter.JSONS_PATH, project_name))
    jw.create({
      jw.DISTRICT : district,
      jw.INSTANCE : instance,
      jw.SPECIALITY : speciality,
      jw.YEAR : year,
      jw.STARTING_FILE_NO: starting_file_no,
      jw.ENDING_FILE_NO: ending_file_no,
      jw.EXCEL_FILE_NAME: excel_file_name,
      jw.OVERWRITE: overwrite,
      jw.FILES: files,
      jw.BOTS: bots, 
    }, jw.META)



