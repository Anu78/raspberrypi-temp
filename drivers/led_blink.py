import RPi.GPIO as gp
import time

ledPin = 17
gp.setmode(gp.BCM)
gp.setup(ledPin, gp.OUT)

while True:
    gp.output(ledPin, gp.HIGH)
    time.sleep(1)
    gp.output(ledPin, gp.LOW)
    time.sleep(1)
gp.cleanup()
