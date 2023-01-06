import torch
import os

CLASSES = ['M','Y','8','9','F','B','V','I','Q','H','4','P','T',
'C','W','A','K','G','N','L','5','6','2','0','Z','7','1','J','D','E',
'O','X','3','R']

PROJECT_BASE = os.getcwd()
IMAGES_PATH = os.path.join(PROJECT_BASE, "images")
MODEL_PATH = os.path.join(PROJECT_BASE, "captcha_model.pt")

model = None

def start():
  global model  
  model = torch.hub.load("WongKinYiu/yolov7","custom", MODEL_PATH, trust_repo=True)

def run(id):
  global model
  img = f"{IMAGES_PATH}\\captcha_{id}.png"

  results = model(img, size = 640)
  predictions = results.pred[0]
  boxes = list(predictions[:, :4])
  categories = [int(x) for x in list(predictions[:, 5])]

  string = ''
  cat_and_pos = []

  for i in range(len(categories)):
    box = boxes[i]
    cat = CLASSES[categories[i]]
    cat_and_pos.append((cat, float(box[0])))

  cat_and_pos.sort(key= lambda x: x[1])

  for cat,_ in cat_and_pos:
    string+=cat

  string = string.replace("O", "0")
  print(f"Crawler {id}'s CAPTCHA: {string}")
  return string
