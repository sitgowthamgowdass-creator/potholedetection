from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import cv2
import uuid
import os

# ⚠️ Comment YOLO for now (Render free plan struggles)
# from ultralytics import YOLO
# model = YOLO("yolov8n.pt")

app = Flask(__name__)
CORS(app, supports_credentials=True)

UPLOAD_FOLDER = "static"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

all_data = []

# ✅ serve images
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

        # 🔴 TEMP: Fake detection (since YOLO removed)
        h, w, _ = img.shape

        x1, y1 = int(w * 0.3), int(h * 0.3)
        x2, y2 = int(w * 0.6), int(h * 0.6)

        width = x2 - x1
        height = y2 - y1

        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)

        cv2.putText(
            img,
            f"W:{width} H:{height}",
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2
        )

        potholes = [{
            "lat": lat,
            "lon": lon,
            "width": width,
            "height": height
        }]

        count = 1

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


# ✅ IMPORTANT FOR RENDER
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
