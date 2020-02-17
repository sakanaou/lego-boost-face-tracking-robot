import logging
import time

import tflite_runtime.interpreter as tflite
import numpy as np
from PIL import Image

from bounding_box import BoundingBox

class TFLiteDetector:

    def __init__(self, interestedClasses=[0], scoreThreshold=0.4):
        self._interpreter = tflite.Interpreter(model_path = "coco_ssd_mobilenet_v1_1.0_quant_2018_06_29/detect.tflite")
        self._interpreter.allocate_tensors()
        _, self._inputHeight, self._inputWidth, _ = self._interpreter.get_input_details()[0]['shape']
        self._scoreThreshold = scoreThreshold
        self._interestedClasses = interestedClasses

    def detect(self, image):
        resizedImage = Image.fromarray(image).resize((self._inputWidth, self._inputHeight), Image.ANTIALIAS)

        self._setInputTensor(resizedImage)

        startTime = time.monotonic()
        self._interpreter.invoke()
        elapsedTime = (time.monotonic() - startTime) * 1000
        logging.info("%.0f ms", elapsedTime)

        boxes = self._getOutputTensor(0)
        classes = self._getOutputTensor(1)
        scores = self._getOutputTensor(2)
        count = int(self._getOutputTensor(3))

        results = []
        for i in range(count):
            if scores[i] < self._scoreThreshold:
                continue

            if classes[i] not in self._interestedClasses:
                continue

            ymin, xmin, ymax, xmax = boxes[i]
            xmin = int(xmin * image.shape[1])
            xmax = int(xmax * image.shape[1])
            ymin = int(ymin * image.shape[0])
            ymax = int(ymax * image.shape[0])

            results.append(BoundingBox(xmin, ymin, xmax, ymax))
        return results

    def _setInputTensor(self, image):
        tensor_index = self._interpreter.get_input_details()[0]['index']
        input_tensor = self._interpreter.tensor(tensor_index)()[0]
        input_tensor[:, :] = image

    def _getOutputTensor(self, index):
        output_details = self._interpreter.get_output_details()[index]
        tensor = np.squeeze(self._interpreter.get_tensor(output_details['index']))
        return tensor
