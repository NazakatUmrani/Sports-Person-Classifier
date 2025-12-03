from flask import Flask, jsonify, request
from flask_cors import CORS
import util
import os

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def hello_world():
    return 'Hello World!'

# Predict price route
@app.route('/classify_image', methods=['POST'])
def classify_image():
    try:
        print(request)
        data = request.get_json()
        image = data['image']
        
        # If image is not base64 encoded, return error
        if not util.is_base64(image):
            raise ValueError("Image is not base64 encoded")
        
        estimated_result = util.classify_image(image)
        
        res = jsonify({
            'result': estimated_result,
            'num_to_person': util.get_num_to_person()
        })
        return res
    except Exception as e:
        print(e)
        res = jsonify({
            'error': str(e)
        })
        return res, 400

if __name__ == '__main__':
    print("Starting Python Flask Server for Real Estate Price Prediction...")
    util.load_saved_artifacts()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)