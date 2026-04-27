from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from ultralytics import YOLO
import cv2
import uuid
import os

app = Flask(__name__)
CORS(app)

# 👉 Use your trained model later (best.pt)
model = YOLO("yolov8n.pt")

UPLOAD_FOLDER = "static"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

all_data = []

# 🔥 serve images
@app.route('/static/<path:filename>')
def serve_image(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/detect', methods=['POST'])
def detect():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image"}), 400

        file = request.files['image']

        lat = float(request.form.get('lat', 12.9716))
        lon = float(request.form.get('lon', 77.5946))

        filename = str(uuid.uuid4()) + ".jpg"
        path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(path)

        img = cv2.imread(path)

        results = model(path, conf=0.2)

        count = 0
        potholes = []

        for r in results:
            for box in r.boxes:
                count += 1

                x1, y1, x2, y2 = map(int, box.xyxy[0])

                # expand box
                padding = 25
                x1 = max(0, x1 - padding)
                y1 = max(0, y1 - padding)
                x2 = x2 + padding
                y2 = y2 + padding

                width = x2 - x1
                height = y2 - y1
                area = width * height

                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)

                cv2.putText(
                    img,
                    f"W:{width} H:{height}",
                    (x1, max(40, y1)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 255),
                    2
                )

                potholes.append({
                    "lat": lat + (y1 / 10000),
                    "lon": lon + (x1 / 10000),
                    "width": width,
                    "height": height,
                    "area": area
                })

        # save processed image
        cv2.imwrite(path, img)

        entry = {
            "count": count,
            "lat": lat,
            "lon": lon,
            "image": f"static/{filename}",
            "potholes": potholes
        }

        all_data.append(entry)

        return jsonify(entry)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/data', methods=['GET'])
def data():
    return jsonify(all_data)


app.run(host='0.0.0.0', port=5000)