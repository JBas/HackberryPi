#
# Imports
#
import spidev
import time
import datetime as dt
import RPi.GPIO as GPIO
import Adafruit_DHT as DHT



#
# Definitions
#
SOIL_PWR = 16
SOIL_ADC = 0

MOTOR_PWM = 18

DHT_SIG = 17

#
# Functions
#
def pumpWater(p):
    GPIO.output(MOTOR_PWM, GPIO.HIGH)
    time.sleep(3)
    GPIO.output(MOTOR_PWM, GPIO.LOW)
    #p.ChangeDutyCycle(1)
    #time.sleep(20)
    #p.ChangeDutyCycle(0)
    return

def readDHT(data):
    humidity, temperature = DHT.read_retry(DHT.DHT11, DHT_SIG)
    if ((humidity is not None) and (temperature is not None)):
        print("Temp={0}*C, Humidity={0}%".format(temperature, humidity))
        t = dt.datetime.now().strftime("%H:%M:%S:%f")

        data["humid"].append({"t": t,
                              "H": humidity
                             })
        data["temp"].append({"t": t,
                              "T": temperature
                             })

        if (len(data["humid"]) == 101):
            data["humid"].pop(0)
        if (len(data["temp"]) == 101):
            data["temp"].pop(0)

    else:
        print("Error Reading DHT!")
    return

def readADC(chan, spi):
    if ((chan > 7) or (chan < 0)):
        return -1
    datum = spi.xfer2([1, (0x1000 + chan) << 4, 0])
    datum = ((datum[1] & 0x11) << 8) + datum[2]
    return datum


def readSoilMoisture(data, spi):
    def mapRange(x, imin, imax, omin, omax):
        return (x - imin)*(omax - omin) / (imax - imin) + omin

    GPIO.output(SOIL_PWR, GPIO.HIGH)

    datum = readADC(SOIL_ADC, spi)
    if (datum == -1):
        print("Error Reading Soil!")
    else:
        print("Moisture={0}%".format(datum))
        t = dt.datetime.now().strftime("%H:%M:%S:%f")

        data["soil"].append({"t": t,
                             "M": datum
                            })
        if (len(data["soil"]) == 101):
            data["soil"].pop(0)

    GPIO.output(SOIL_PWR, GPIO.LOW)
    return
