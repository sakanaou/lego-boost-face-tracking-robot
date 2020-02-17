import logging
from argparse import ArgumentParser
from enum import Enum
from operator import methodcaller

import cv2
from matplotlib import pyplot
from threading import Thread

from cv_detector import CVDetector
from tflite_detector import TFLiteDetector
from bounding_box import BoundingBox

logging.basicConfig(level = logging.INFO)
currentImage = None

class DetectorType(Enum):
    cv = "cv"
    tflite = "tflite"

    def __str__(self):
        return self.value

parser = ArgumentParser()
parser.add_argument("--detector",
    help="Specify the detector to use.",
    type=DetectorType,
    choices=list(DetectorType),
    required=False,
    default=DetectorType.cv)
parser.add_argument("--camera",
    help="Specify which camera to use.",
    type=int,
    required=False,
    default=0)
args = parser.parse_args()

def capture():
    global currentImage

    logging.info("Starting cam %d...", args.camera)
    videoCam = cv2.VideoCapture(args.camera)
    videoCam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    videoCam.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)

    try:
        while True:
            _, image = videoCam.read()
            currentImage = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            logging.debug("Got frame")
    finally:
        logging.info("Releasing cam...")
        videoCam.release()

thr = Thread(target = capture)
thr.setDaemon(True)
thr.start()

while currentImage is None:
    pass

plt = pyplot.imshow(currentImage)
pyplot.tight_layout()
pyplot.ion()
pyplot.show()

if args.detector == DetectorType.cv:
    detector = CVDetector()
elif args.detector == DetectorType.tflite:
    detector = TFLiteDetector()

try:
    while thr.is_alive():
        boundingBoxes = detector.detect(currentImage)
        boundingBoxes = sorted(boundingBoxes, key=methodcaller("surface"), reverse=True)

        for i, boundingBox in enumerate(boundingBoxes):
            if i == 0:
                color = (0, 255, 0,)
            else:
                color = (255, 0, 0,)
            cv2.rectangle(currentImage,
                (boundingBox.xmin, boundingBox.ymin),
                (boundingBox.xmax, boundingBox.ymax),
                color, 2)

            if i == 0:
                center = boundingBox.center()
                imageCenter = (int(currentImage.shape[1] / 2), int(currentImage.shape[0] / 2))
                cv2.line(currentImage, center, imageCenter, (0, 0, 255,), 2)
                logging.info("Robot has to move by %s", (abs(imageCenter[0] - center[0]), abs(imageCenter[1] - center[1])))

        plt.set_array(currentImage)
        logging.debug("Updated frame")
        pyplot.pause(0.02)
finally:
    pass
