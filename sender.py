import requests
import os
import time

url = "https://potholedetection-mqs9.onrender.com/detect"

IMAGE_FOLDER = "images"   # put your images here

for img_name in os.listdir(IMAGE_FOLDER):
    path = os.path.join(IMAGE_FOLDER, img_name)

    if path.endswith(".jpg") or path.endswith(".png"):
        print("Sending:", img_name)

        files = {"image": open(path, "rb")}
        data = {
            "lat": 12.9716,
            "lon": 77.5946
        }

        res = requests.post(url, files=files, data=data)
        print(res.json())

        time.sleep(2)
