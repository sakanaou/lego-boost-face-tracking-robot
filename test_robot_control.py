from time import sleep
import logging

from robot_control import RobotControl

logging.basicConfig(level = logging.INFO)

rbtCtrl = RobotControl()

sleep(1)
rbtCtrl.moveLeft()
sleep(1)
rbtCtrl.moveRight()
sleep(1)
rbtCtrl.moveUp()
sleep(1)
rbtCtrl.moveDown()

del rbtCtrl
