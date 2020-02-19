A Lego Boost based face tracking robot
======================================

This repository holds the source code for a Lego Boost based robot which does face tracking via OpenCV or TensorFlow Lite.
The robot will be part of our booth at the JAX 2020.

The face detection will be done via OpenCV or a pre-trained Machine Learning model via TensorFlow Lite. To speed up the inferencing of the ML model support for the Google Coral AI Edge TPU Accelerator is provided.

Prerequisites
-------------
Prior execution ensure that the dependencies are installed via
```
pip install -r requirements.txt
```
By default the OpenCV-based face detector will be used.

If you want to use the TensorFlow Lite detector (enabled via `--detector tflite`) install the appropiate extension as described here:
https://www.tensorflow.org/lite/guide/python

If you want to use the Google Coral AI Edge TPU Accelerator (enabled via `--detector edgetpu`) install its driver and the appropiate extension as described here:
* https://coral.ai/docs/accelerator/get-started/
* https://www.tensorflow.org/lite/guide/python

Machine Learning model
----------------------
The TensorFlow Lite version makes uses of a pre-trained and pre-compiled model available here:
* http://storage.googleapis.com/download.tensorflow.org/models/tflite/coco_ssd_mobilenet_v1_1.0_quant_2018_06_29.zip
* https://dl.google.com/coral/canned_models/coco_labels.txt

Credits
-------
The project is heavily inspired by
* https://github.com/undera/pylgbst/tree/master/examples/tracker
* https://github.com/tensorflow/examples/tree/master/lite/examples/object_detection/raspberry_pi
