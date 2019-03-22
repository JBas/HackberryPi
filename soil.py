import RPi.GPIO as GPIO
import time
import config

GPIO.setmode(GPIO.BOARD)

GPIO.setup(config.soilPwr, GPIO.OUTPUT)

try:
    while (True):
        if (config.read):
            GPIO.output(config.soilPwr, GPIO.HIGH)
            while (not config.adc_done):
                continue
            # data is ready
        GPIO.output(config.soilPwr, GPIO.LOW)
except KeyboardInterrupt:
    GPIO.cleanup()
