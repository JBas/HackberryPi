import spidev
import time
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import Adafruit_DHT
import RPi.GPIO as GPIO


def readADC(chan, spi):
    if ((chan > 7) or (chan < 0)):
        return -1

    datum = spi.xfer2([1, (0x1000 + chan) << 4, 0])
    return datum

def testADC():
    spi = spidev.SpiDev()
    spi.open(0, 0)
    try:
        while (True):
            print("{0}\n".format(readADC(0, spi)))
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nClosing!\n")
    finally:
        spi.close()

def testPlotter():
    plt.plot([1, 2, 3, 4])
    plt.ylabel("some numbers")
    plt.show()

def testDHT():
    while (True):
        humidity, temperature = Adafruit_DHT.read_retry(11, 7)
        print("Temp: {0:0.1f} C  Humidity: {1:0.1f} %".format(temperature, humidity))
        time.sleep(1)
    return

def testButton():
    def myCall(i):
        print("HEY")
        return
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(25, GPIO.FALLING, callback=myCall, bouncetime=200) 
    try:
        while (True):
            continue
    except:
        GPIO.cleanup()

def testMotor():
    GPIO.setmode(GPIO.BCM)
    p = GPIO.(18, 1)
    p.start(0.50)
    time.sleep(5)
    p.stop()
    GPIO.cleanup()

testMotor()



