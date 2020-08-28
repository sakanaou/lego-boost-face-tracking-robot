import logging
from argparse import ArgumentParser
from enum import Enum
from operator import methodcaller

import cv2
from matplotlib import pyplot
from threading import Thread

from cv_detector import CVDetector
from tflite_detector import TFLiteDetector, EdgeTpuDetector
from bounding_box import BoundingBox

from robot_control import RobotControl

logging.basicConfig(level = logging.INFO)
currentImage = None

class DetectorType(Enum):
    cv = "cv"
    tflite = "tflite"
    edgetpu = "edgetpu"

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
parser.add_argument("--classes-of-interest",
    help="List all classes of interest for the TensorFlow Lite based detectors.",
    type=int,
    nargs="+",
    required=False,
    default=[0])
parser.add_argument("--score-threshold",
    help="The scoring threshold for the TensorFlow Lite based detectors.",
    type=float,
    required=False,
    default=0.4)
parser.add_argument("--robot-control",
    help="Enable robot control.",
    type=bool,
    required=False,
    default=False)
parser.add_argument("--robot-mac",
    help="Specify the robot's MAC address.",
    type=str,
    required=False,
    default=None)
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

detector = {
    DetectorType.cv: CVDetector(),
    DetectorType.tflite: TFLiteDetector(args.classes_of_interest, args.score_threshold),
    DetectorType.edgetpu: EdgeTpuDetector(args.classes_of_interest, args.score_threshold)
}[args.detector]

detector.setup()

robotControl = None
if args.robot_control:
    robotControl = RobotControl(args.robot_mac)

try:
    while thr.is_alive():
        boundingBoxes = detector.detect(currentImage)
        boundingBoxes = sorted(boundingBoxes, key=methodcaller("surface"), reverse=True)

        if robotControl and not boundingBoxes:
            robotControl.stop()

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

                horizontal = (center[0] - imageCenter[0]) / currentImage.shape[1]
                vertical = (center[1] - imageCenter[1]) / currentImage.shape[0]
                logging.info("Robot has to move by %.3f, %.3f", horizontal, vertical)
                if robotControl:
                    if abs(horizontal) > 0.075:
                        if horizontal < 0:
                            robotControl.moveRight()
                        elif horizontal > 0:
                            robotControl.moveLeft()
                    else:
                        robotControl.stopHorizontalMovement()
                    if abs(vertical) > 0.075:
                        if vertical < 0:
                            robotControl.moveUp()
                        elif vertical > 0:
                            robotControl.moveDown()
                    else:
                        robotControl.stopVerticalMovement()

        plt.set_array(currentImage)
        logging.debug("Updated frame")
        pyplot.pause(0.02)
finally:
    if robotControl:
        del robotControl
    pass
