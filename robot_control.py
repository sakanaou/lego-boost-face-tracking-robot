import logging
import time

from pylgbst.comms.cpygatt import BlueGigaConnection
from pylgbst import *
from pylgbst.hub import MoveHub
from pylgbst.peripherals import EncodedMotor, Current, Voltage

log = logging.getLogger('RobotControl')

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

    def __del__(self):
        log.info("Releasing LEGO Move Hub connection...")
        self.conn.disconnect()

    def moveLeft(self):
        if self.motor:
            log.info("Moving LEGO Boost robot to the LEFT")
            self.motor.angled(60, 0.05)
        return

    def moveRight(self):
        if self.motor:
            log.info("Moving LEGO Boost robot to the RIGHT")
            self.motor.angled(-60, 0.05)
        return

    def moveUp(self):
        log.info("Moving LEGO Boost robot UP")
        self.hub.motor_AB.angled(8, 0.05)
        return

    def moveDown(self):
        log.info("Moving LEGO Boost robot DOWN")
        self.hub.motor_AB.angled(-10, 0.05)
        return

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
