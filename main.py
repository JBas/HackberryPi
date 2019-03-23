import time
import datetime as dt
import json
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import RPi.GPIO as GPIO
import spidev
import Adafruit_DHT as DHT

#-----------------------Definitions-----------------------#
# Based on GPIO.BOARD mode

soilPwr = 11 # provides power to sensor
soil_adc = 0 # MCP3008 channel

#dhtPwr = 13 # provides power to sensor
dht_sig = 17 # grabs sensor data


# SPI interface
spi = spidev.SpiDev()

# Experimentally defined min, max values
imin = 1
imax = 1
omin = 1
omax = 1
    
# matplotlib setup
fig = plt.figure()
ax1 = fig.add_subplot(3, 1, 1)
ax2 = fig.add_subplot(3, 1, 2)
ax3 = fig.add_subplot(3, 1, 3)

#--------------------Thread Functions--------------------#

def readDHT(xp_humid, yp_humid, xp_temp, yp_temp):
    # read temp/humid data
    humidity, temperature = DHT.read_retry(DHT.DHT11, dht_sig)
    if ((humidity is not None) and (temperature is not None)):
        #print("Temp={0:0.1f}*, Humidity={0:0.1f}%\n".format(temperature, humidity))
        t = dt.datetime.now().strftime("%H:%M:%S:%f")
        xp_humid.append(t)
        xp_humid = xp_humid[-100:]

        yp_humid.append(humidity)
        yp_humid = yp_humid[-100:]

        yp_temp.append(temperature)
        yp_temp = yp_temp[-100:]
                    
        xp_temp.append(t)
        xp_temp = xp_temp[-100:]
    else:
        print("Error Reading DHT!\n")
    return

def readSoilMoisture(xp_soil, yp_soil):
    def mapRange(x, imin, imax, omin, omax):
        return (x - imin)*(omax - omin) / (imax - imin) + omin

    # read soil moisture data
    GPIO.output(soilPwr, GPIO.HIGH)
    data = readADC(soil_adc)
    if (data == -1):
        print("Error Reading Soil!\n")
    else:
        #data = mapRange(data,
        #config.imin, config.imax,
        #config.omin, config.omax)
        #print("Moisture={0:0.1f}".format(data))
        yp_soil.append(data)
        yp_soil = yp_soil[-100:]

        t = dt.datetime.now().strftime("%H:%M")
        xp_soil.append(t)
        xp_soil = xp_soil[-100:]

    GPIO.output(soilPwr, GPIO.LOW)
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

def plotData(xp_humid, yp_humid, xp_temp, yp_tmep, xp_soil, yp_soil):
    ax1.clear()
    ax1.plot(xp_soil, yp_soil)
    ax1.set(xlabel="time", ylabel="voltage",
            title="Soil Moisture v Time")

    ax2.clear()
    ax2.plot(xp_temp, yp_temp)
    ax2.set(xlabel="time", ylabel="voltage",
            title="Temperature v Time")

    ax3.clear()
    ax3.plot(xp_humid, yp_humid)
    ax3.set(xlabel="time", ylabel="voltage",
            title="Humidity v Time")

def saveData():
    with open("data.txt", "wb") as file:
        json.dump(xp_temp, file)
        json.dump(yp_temp, file)
        json.dump(xp_humid, file)
        json.dump(yp_humid, file)
        json.dump(xp_soil, file)
        json.dump(yp_soil, file)


def main():
    # data arrays
    xp_soil = []
    yp_soil = []

    xp_temp = []
    yp_temp = []

    xp_humid = []
    yp_humid = []

    spi.open(0, 0)
    GPIO.setmode(GPIO.BOARD)

    GPIO.setup(soilPwr, GPIO.OUTPUT)
    GPIO.output(soilPwr, GPIO.LOW)

    try:

        while (True):
            readDHT(xp_humid, yp_humid, xp_temp, yp_temp)
            readSoilMoisture(xp_soil, yp_soil)
            plotData(xp_humid, yp_humid, xp_temp, yp_tmep, xp_soil, yp_soil)
            plt.show()
    except KeyboardInterrupt:
        print("Thank you for using our design!")
        time.sleep(500)
        print("Goodbye!")
    finally:
        saveData()
        spi.close()
        GPIO.cleanup()
    return

if __name__ == "__main__":
    main()
