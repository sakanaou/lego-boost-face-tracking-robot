import logging
import time

import cv2

from bounding_box import BoundingBox

class CVDetector:

    def setup(self):
        self._faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    def detect(self, image):
        startTime = time.monotonic()
        bodies, _, weights = self._faceCascade.detectMultiScale3(image, 1.5, 5, outputRejectLevels=True)
        elapsedTime = (time.monotonic() - startTime) * 1000
        logging.info("%.0f ms", elapsedTime)

        if len(bodies):
            logging.debug("Bodies: %s / Weights: %s", bodies, weights)
        else:
            return []

        results = []
        for x, y, w, h in bodies:
            results.append(BoundingBox(x, y, x + w, y + h))

        return results
