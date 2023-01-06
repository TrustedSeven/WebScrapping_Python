from package.crawler import Crawler
from package.scraper import Scraper
from package.smart_writer import SmartWriter
from package.json_writer import JsonWriter
import package.detection as dt

from multiprocessing import Pool
import multiprocessing
import keyboard


import numpy as np
import os
import time

class EndTask(Exception):
  pass

def generate_bots(core_count, files: list = None):
  bots = [  ]
  cores = core_count
  
  if len(files) < cores:
    count = 1
  else:
    count = cores


  split_files = np.array_split(files, count)
  for i in range(count):
    bot = {
      "id" : i + 1,
      "files" : [int(x) for x in split_files[i]],
      "completed" : False,
    }

    bots.append(bot)

  return bots


def main_loop(project_name, meta_data , bot, _context):
  # try:
    jw = JsonWriter(project_name)
    jw.file_name = f"{bot['id']}.json"

    if _context == "old":
      bot_data = jw.read()
      files = bot_data[jw.FILES]
      done_files = bot_data[jw.DONE_FILES]
      captcha_failed = bot_data[jw.CAPTCHA_FAILED]
      data = bot_data[jw.DATA]
      completed = bot_data[jw.COMPLETED]
    else:
      bot_data = {
        jw.ID: bot["id"],
        jw.FILES: bot["files"],
        jw.DONE_FILES: [],
        jw.CAPTCHA_FAILED: [],
        jw.DATA: [],
        jw.COMPLETED: False,
      }
      jw.create(bot_data, f"{bot['id']}.json")
      bot_data = jw.read()
      files = bot_data[jw.FILES]
      done_files = bot_data[jw.DONE_FILES]
      captcha_failed = bot_data[jw.CAPTCHA_FAILED]
      data = bot_data[jw.DATA]
      completed = bot_data[jw.COMPLETED]


    
    district = meta_data[jw.DISTRICT]
    instance = meta_data[jw.INSTANCE]
    speciality = meta_data[jw.SPECIALITY]
    year = meta_data[jw.YEAR]

    print("Starting the captcha model.")
    dt.start()
    print("Done")
    crawler = Crawler(bot["id"], self_init=False, headless=True)
    scraper = Scraper(crawler.driver, bot["id"])
    files.extend(captcha_failed)
    _ = [files.remove(x) for x in done_files]
    to_do_files = files.copy()
    crawler.initialize()
    context = None
    for file_num in to_do_files:
      # file_num = starting_file_no + file_num - 1
      row = None
      print()
      print(f"Scraping file no. {file_num}")
      response = crawler.fill_form(
        district, instance, speciality, year, str(file_num), context
      )
      context = response
      if response == crawler.NO_RECORD:
        print(f"File no. {file_num} not found.")
        row = ["NO RECORD", district, instance, speciality, "", int(year), str(file_num)]
        data.append(row)
        jw.change_field(jw.DATA, data)
        done_files.append(file_num)
        jw.change_field(jw.DONE_FILES, done_files)
        # print(row)
        # if not writer.is_busy:
        #   writer.write_row(row)
        # else:
        #   writer.receive_row(row)
      elif response == crawler.CAPTCHA_FAIL:
        print(f"Captcha failed for file no. {file_num}")
        row = ["CAPTCHA FAIL", district, instance, speciality, "", int(year), str(file_num)]  
        data.append(row)
        jw.change_field(jw.DATA, data)
        done_files.append(file_num)
        jw.change_field(jw.DONE_FILES, done_files)
        captcha_failed.append(file_num)
        jw.change_field(jw.CAPTCHA_FAILED, captcha_failed)
        # print(row)
        # if not writer.is_busy:
        #   writer.write_row(row)
        # else:
        #   writer.receive_row(row)# writer.save()
      elif response == crawler.CAPTCHA_PASS:
        was_last = False
        index = 0
        demandas = scraper.scrape_records_page()
        while not was_last:
          was_last = crawler.open_file(index)
          main_info = scraper.get_main_info()
          follow_ups = scraper.get_follow_ups()
          demandante, demandado = demandas[index]
          main_info.append(demandante)
          main_info.append(demandado)
          index += 1
          if not was_last:
            crawler.go_back()
          row = main_info + follow_ups
          data.append(row)
          jw.change_field(jw.DATA, data)
          done_files.append(file_num)
          jw.change_field(jw.DONE_FILES, done_files)
        crawler.home_page()
      print(f"Crawler {bot['id']} files completed: {len(done_files)}/{len(bot_data[jw.FILES])}")

    jw.change_field(jw.COMPLETED, True)
    crawler.close()  

  # except Exception as e:
    # raise e

  

if __name__ == "__main__":
  print()
  print("PROYECTO DE WEB SCRAPING")
  print("========================")
  print()
  print("Website: https://cej.pj.gob.pe/cej/forms/busquedaform.html")
  print()
  old_or_new = input("Do you wish to run a previously incomplete session or a completely new session? (old/new) ").lower()
  if old_or_new[0] == "o":
    context = "old"
    incomplete = os.listdir(JsonWriter.JSONS_PATH)
    if len(incomplete) == 0:
      print("No incomplete projects found.")
      quit()
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
      core_count = meta_data[jw.CORE_COUNT]

  else:
    context = "new"
    district = input("Ingresar 'Distrito Judicial': ").upper()
    instance = input("Ingresar 'Instancia': ").upper()
    speciality = input("Ingresar 'Especialidad': ").upper()
    year = input("Ingresar 'Año': ").upper()
    starting_file_no = int(input("N° Expediente inicial: "))
    ending_file_no = int(input("N° Expediente final: "))
    project_name = input("Nombre de Proyecto: ")
    core_count = input(f"Enter the number of cores to use. Leave blank for default i.e {os.cpu_count()}) ")
    if core_count == "":
      core_count = os.cpu_count()
    else:
      core_count = int(core_count)
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
    bots = generate_bots(core_count, files)
    # bots = [{"id":1, "files": files, "completed":False}]
    jw = JsonWriter(project_name)
    try:
      os.mkdir(os.path.join(JsonWriter.JSONS_PATH, project_name))
    except:
      pass
    meta_data = {
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
      jw.CORE_COUNT: core_count,
    }
    jw.create(meta_data, jw.META)

  # logger = multiprocessing.log_to_stderr()
  # logger.setLevel(multiprocessing.SUBDEBUG)
  print("PRESS 'Ctrl + C' TO QUIT DURING EXECUTION. PROGRESS WILL NOT BE LOST.")
  time.sleep(3)
  # main_loop(project_name, meta_data, bots[0], context)
  t1 = time.time()  
  Pool(len(bots)).starmap(main_loop, [(project_name, meta_data,bot, context) for bot in bots])  
  sw = SmartWriter(excel_file_name, overwrite)
  data = jw.get_all_subprocess_data()
  for row in data:
    sw.write_row(row)
  sw.sort()
  sw.save()
  for file in os.listdir(jw.project_path):
    os.remove(os.path.join(jw.project_path, file))
  os.rmdir(jw.project_path)

  print(f"Scraped {len(meta_data[jw.FILES])} in {time.time() - t1} seconds.")
  print(f"Excel file saved as {dt.PROJECT_BASE}/workbooks/{excel_file_name}")


