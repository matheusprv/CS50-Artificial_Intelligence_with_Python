from model import model
import numpy

# Observed data
observations = [
    "umbrella",
    "umbrella",
    "no umbrella",
    "umbrella",
    "umbrella",
    "umbrella",
    "umbrella",
    "no umbrella",
    "no umbrella"
]

observations = numpy.array([[[['umbrella', 'no umbrella'].index(char)] for char in observations]])

# Predict underlying states
predictions = model.predict(observations).tolist()[0]

prediction_dict = {0: "sun", 1: "rain"} # Baseado na ordem das categorias do model.py

for prediction in predictions:
   print(prediction_dict[prediction])
