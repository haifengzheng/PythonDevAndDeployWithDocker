import os
import base64
import json
import falcon
import numpy as np
from io import BytesIO
from PIL import Image, ImageOps

from keras.models import load_model


def convert_image(image):
    img = Image.open(image).convert('L')
    inverted_img = ImageOps.invert(img)
    data = np.asarray(inverted_img, dtype='int32')
    rescaled_data = (data / 255).reshape(1, 28, 28, 1)
    return rescaled_data

class HealthResource():
    def __init__(self):
        pass
    
    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
        resp.body = 'I\'m alive.'

class PredictResource():

    def __init__(self, model):
        self.model = model

    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200
        resp.body = 'Hello World!'

    def on_post(self, req, resp):
        """
        (echo -n '{"image": "'; four_test.png; echo '"}') |
        curl -H "Content-Type: application/json" -d @-  http://127.0.0.1:8000/predict
        """
        image = json.loads(req.stream.read())
        decoded_image = base64.b64decode(image.get('image'))
        data = convert_image(BytesIO(decoded_image))
        predicted_data = self.model.predict_classes(data)[0]

        output = {'prediction': str(predicted_data)}
        resp.status = falcon.HTTP_200
        resp.body = json.dumps(output, ensure_ascii=False)



def load_trained_model():
    global model
    model = load_model(os.path.join(os.path.dirname(__file__), 'model/cnn_model.h5'))
    model._make_predict_function()
    return model

# Instantiation resources
healthResource = HealthResource()
predictResource = PredictResource(model = load_trained_model())

# Create API and attach resources to endpoints
api = application = falcon.API()
api.add_route('/health', healthResource)
api.add_route('/predict', predictResource)
