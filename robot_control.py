import logging
from enum import Enum

from pylgbst.comms.cpygatt import BlueGigaConnection
from pylgbst import *
from pylgbst.hub import MoveHub
from pylgbst.peripherals import EncodedMotor, Current, Voltage

log = logging.getLogger('RobotControl')

class Direction(Enum):
    LEFT = "left",
    RIGHT = "right",
    UP = "up",
    DOWN = "down"

class RobotControl:
    def __init__(self, hub_mac=None):
        log.info("Searching for LEGO Move Hub (using MAC %s)...", hub_mac)
        self.conn = BlueGigaConnection()
        if hub_mac == None:
            self.conn.connect(hub_name="LEGO Move Hub")
        else:
            self.conn.connect(hub_mac)
        self.hub = MoveHub(self.conn)
        log.info("Connected to LEGO Move Hub!")
        self._detect_motor()
        self.motor_running = None
        self.motorA_running = None

    def __del__(self):
        self.stop()
        log.info("Releasing LEGO Move Hub connection...")
        self.conn.disconnect()

    def moveLeft(self, speed=0.15):
        if self.motor and self.motor_running != Direction.LEFT:
            log.info("Moving LEGO Boost robot to the LEFT")
            if self.motor_running == Direction.RIGHT:
                self.motor.stop()
            self.motor.start_speed(speed)
            self.motor_running = Direction.LEFT
        return

    def moveRight(self, speed=-0.15):
        if self.motor and self.motor_running != Direction.RIGHT:
            log.info("Moving LEGO Boost robot to the RIGHT")
            if self.motor_running == Direction.LEFT:
                self.motor.stop()
            self.motor.start_speed(speed)
            self.motor_running = Direction.RIGHT
        return

    def moveUp(self, speed=-0.15):
        if self.motorA_running != Direction.UP:
            log.info("Moving LEGO Boost robot UP")
            if self.motor_running == Direction.DOWN:
                self.hub.motor_A.stop()
            self.hub.motor_A.start_speed(speed)
            self.motorA_running = Direction.UP
        return

    def moveDown(self, speed=0.15):
        if self.motorA_running != Direction.DOWN:
            log.info("Moving LEGO Boost robot DOWN")
            if self.motor_running == Direction.UP:
                self.hub.motor_A.stop()
            self.hub.motor_A.start_speed(speed)
            self.motorA_running = Direction.DOWN
        return

    def stopHorizontalMovement(self):
        if self.motor and self.motor_running:
            self.motor.stop()
        self.motor_running = None

    def stopVerticalMovement(self):
        if self.motorA_running:
            self.hub.motor_A.stop()
        self.motorA_running = None

    def stop(self):
        self.stopHorizontalMovement()
        self.stopVerticalMovement()

    def _detect_motor(self):
        self.motor = None
        if isinstance(self.hub.port_C, EncodedMotor):
            log.info("Rotation motor is on port C")
            self.motor = self.hub.port_C
        elif isinstance(self.hub.port_D, EncodedMotor):
            log.info("Rotation motor is on port D")
            self.motor = self.hub.port_D
        else:
            log.warning("Motor not found on ports C or D")
