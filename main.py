#------------------------Imports-------------------------#
from threading import Lock
import spidev
import time
import datetime as dt
import json
from pprint import pprint
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import RPi.GPIO as GPIO
import Adafruit_DHT as DHT

#-----------------------Definitions-----------------------#

SOIL_PWR = 16 # provides power to sensor
SOIL_ADC = 0 # MCP3008 channel
THRESHOLD = 1

MOTOR_PWM = 18
motor_lock = Lock()

DHT_SIG = 17 # grabs sensor data

BTN_PWR = 25
BTN_WATER = 24

# flags
on = True
manWater = False

# SPI interface
spi = spidev.SpiDev()

# Experimentally defined min, max values
#imin = 0
#imax = 820
#omin = 0
#omax = 100
    
# matplotlib setup
fig = plt.figure()
ax1 = fig.add_subplot(3, 1, 1)
ax2 = fig.add_subplot(3, 1, 2)
ax3 = fig.add_subplot(3, 1, 3)

#--------------------Thread Functions--------------------#

def readDHT(data_humid, data_temp):
    # read temp/humid data
    humidity, temperature = DHT.read_retry(DHT.DHT11, DHT_SIG)
    if ((humidity is not None) and (temperature is not None)):
        print("Temp={0:0.1f}*C, Humidity={0:0.1f}%".format(temperature, humidity))
        t = dt.datetime.now().strftime("%H:%M:%S:%f")
        data_humid.append((t, humidity))
        data_humid = data_humid[-100:]

        data_temp.append((t, temperature))
        data_temp = data_temp[-100:]
    else:
        print("Error Reading DHT!")
    return

def readSoilMoisture(data_soil):
    def mapRange(x, imin, imax, omin, omax):
        return (x - imin)*(omax - omin) / (imax - imin) + omin

    # read soil moisture data
    GPIO.output(SOIL_PWR, GPIO.HIGH)
    data = readADC(SOIL_ADC)
    if (data == -1):
        print("Error Reading Soil!")
    else:
        #data = mapRange(data, 0, 820, 0, 100)
        print("Moisture={0}%".format(data))
        t = dt.datetime.now().strftime("%H:%M")
        data_soil.append((t, data))
        data_soil = data_soil[-100:]

    GPIO.output(SOIL_PWR, GPIO.LOW)
    return

def readADC(chan):
    # https://github.com/pimylifeup/Pi-ADC-Example-Code
    if ((chan > 7) or (chan < 0)):
        return -1

    # from MCP3008 datasheet
    # configure bits for channel
    # 1 is the Start bit
    # 0x1000 + chan << 4 are the configure bits
    # 0 is read as dont cares
    # See Section 6.1 for more info
    datum = spi.xfer2([1, (0x1000 + chan) << 4, 0])
    datum = ((datum[1] & 0x11) << 8) + datum[2]
    return datum

def plotData(i, data_humid, data_temp, data_soil, p):
    if (on):
        readDHT(data_humid, data_temp)
        #readSoilMoisture(data_soil)
        waterPlant(p)

        #if (not manWater):
        #    try:
        #        if (data_soil[-1][1] < THRESHOLD):
        #            #motorDriver(p)
        #    except IndexError:
        #        print("Empty List!")
        #else:
        #    water_lock.acquire(blocking=False)
        #    manWater = False
        #    water_lock.release()

        #ax1.clear()
        #ax1.plot(*zip(*data_soil))
        #ax1.set(xlabel="time", ylabel="voltage",
        #        title="Soil Moisture v Time",
        #        xticklabels=[])
        #ax1.tick_params(bottom=False)
        ax1.plot().set_data(*zip(*data_soil));
        ax2.plot().set_data(*zip(*data_temp));
        ax3.plot().set_data(*zip(*data_humid));

        #ax2.clear()
        #ax2.plot(*zip(*data_temp))
        #ax2.set(xlabel="time", ylabel="voltage",
        #        title="Temperature v Time",
        #        xticklabels=[])
        #ax2.tick_params(bottom=False)

        #ax3.clear()
        #ax3.plot(*zip(*data_humid))
        #ax3.set(xlabel="time", ylabel="voltage",
        #        title="Humidity v Time",
        #        xticklabels=[])
        #ax3.tick_params(bottom=False)
    else:
        plt.close()
    return

def saveData(data_humid, data_temp, data_soil):
    with open("data.json", "w") as file:
        json.dump([data_humid, data_temp, data_soil], file)
    with open("data.json") as file:
        pprint(json.load(file))
    return

def waterPlant(p):
    p.ChangeDutyCycle(1)
    time.sleep(5)
    p.ChangeDutyCycle(0)
    return

def main():
    # data arrays
    data_soil = []
    data_temp = []
    data_humid = []

    spi.open(0, 0)
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(BTN_PWR, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(BTN_WATER, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def terminate(i):
        global on
        on = False
        return

    def manualWater(p):
        global manWater
        waterPlant(p)
        water_lock.acquire()
        manWater = True
        water_lock.release()
        return

    GPIO.add_event_detect(BTN_PWR, GPIO.FALLING,
                          callback=terminate, bouncetime=200)
    #GPIO.add_event_detect(BTN_WATER, GPIO.FALLING,
    #                      callback=(lambda x: waterPlant(p)), bouncetime=200)

    #GPIO.setup(SOIL_PWR, GPIO.OUT)
    #GPIO.output(SOIL_PWR, GPIO.LOW)
    GPIO.setup(MOTOR_PWM, GPIO.OUT)
    p = GPIO.PWM(MOTOR_PWM, 0.25)
    p.start(0)

    try:
        ani = animation.FuncAnimation(fig, plotData, interval=2500,
                                        fargs=(data_humid,
                                               data_temp,
                                               data_soil, p))
        plt.show()
    except:
        plt.close("all")
    finally:
        p.stop()
        print("\nThank you!", end=" ")
        spi.close()
        GPIO.cleanup()
        time.sleep(1)
        print(".", end="")
        time.sleep(0.5)
        print(".", end="")
        time.sleep(0.5)
        print(".")
        time.sleep(0.5)
        print("Goodbye!")

        #saveData(data_humid, data_temp, data_soil)
    return

if __name__ == "__main__":
    main()
