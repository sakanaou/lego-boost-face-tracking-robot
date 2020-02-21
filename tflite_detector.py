import logging
import time
import platform

import tflite_runtime.interpreter as tflite
import numpy as np
from PIL import Image

from bounding_box import BoundingBox


EDGETPU_SHARED_LIB = {
  'Linux': 'libedgetpu.so.1',
  'Darwin': 'libedgetpu.1.dylib',
  'Windows': 'edgetpu.dll'
}[platform.system()]


class TFLiteDetector:

    def __init__(self, interestedClasses=[0], scoreThreshold=0.4):
        self._interestedClasses = interestedClasses
        self._scoreThreshold = scoreThreshold

    def setup(self):
        self._interpreter = self._setupInterpreter()
        self._interpreter.allocate_tensors()
        _, self._inputHeight, self._inputWidth, _ = self._interpreter.get_input_details()[0]['shape']

    def _setupInterpreter(self):
        return tflite.Interpreter(model_path="models/mobilenet_ssd_v2_coco_quant_postprocess.tflite")

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


class EdgeTpuDetector(TFLiteDetector):

    def __init__(self, interestedClasses=[0], scoreThreshold=0.4):
        super().__init__(interestedClasses=interestedClasses, scoreThreshold=scoreThreshold)

    def _setupInterpreter(self):
        return tflite.Interpreter(model_path="models/mobilenet_ssd_v2_coco_quant_postprocess_edgetpu.tflite",
            experimental_delegates=[
                tflite.load_delegate(EDGETPU_SHARED_LIB, {})
            ])
