import logging
import cv2
from matplotlib import pyplot
from threading import Thread

logging.basicConfig(level = logging.INFO)
cur_img = None

def capture():
    global cur_img

    logging.info("Starting cam...")
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)

    try:
        while True:
            _, img = cap.read()
            cur_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            logging.debug("Got frame")
    finally:
        logging.info("Releasing cam...")
        cap.release()

thr = Thread(target = capture)
thr.setDaemon(True)
thr.start()

while cur_img is None:
    pass

plt = pyplot.imshow(cur_img)
pyplot.tight_layout()
pyplot.ion()
pyplot.show()

try:
    while thr.is_alive():
        plt.set_array(cur_img)
        logging.debug("Updated frame")
        pyplot.pause(0.02)
finally:
    pass
