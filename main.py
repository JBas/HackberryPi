from threading import Thread
import time
import matplotlib.pyplot as plot
import matplotlib.animation as animation
import RPi.GPIO as GPIO
import spidev
import Adafruit_DHT as DHT

#-----------------------Definitions-----------------------#
# Based on GPIO.BOARD mode

soilPwr = 11 # provides power to sensor
soil_adc = 0 # MCP3008 channel

tempPwr = 13 # provides power to sensor
temp = 29 # grabs sensor data

# boolean to read soil moisture
read = True

# Experimentally defined min, max values
imin = 1
imax = 1
omin = 1
omax = 1

# data arrays
xp_soil = []
yp_soil = []

xp_temp = []
yp_temp = []

xp_humid = []
yp_humid = []

# data locks
soil_lock = Lock()
dht_lock = Lock()

# matplotlib setup
fig = plot.figure()
ax1 = fig.add_subplot(1, 1, 1)
ax2 = fig.add_subplot(1, 1, 2)
ax2 = fig.add_subplot(1, 1, 3)

#--------------------Thread Functions--------------------#

def readDHT():
    try:
        sensor = DHT.DHT11
        while (True):
            # read temp/humid data
            dht_lock.acquire()
            try:
                humidity, temperature = DHT.read_retry(sensor, temp)
                if ((humidity is not None) and (temperature is not None)):
                    print("Temp={0:0.1f}*, Humidity={0:0.1f}%\n".format(temperature, humidity))
                    yp_humid.append(humidity)
                    yp_temp.append(temperature)
                    #time data
                else:
                    print("Error Reading DHT!\n")
            finally:
                dht_lock.release()

            time.sleep(300000) # wait 5 minutes
            i = 1/0
    except KeyboardInterrupt:
        print("Ctrl-C pressed, from DHT!\n")
    except ZeroDivisionError:
        print("Divided by 0, from DHT!\n")
    finally:
        print("DHT closed!\n")
        

def readSoilMoisture():
    def mapRange(x, imin, imax, omin, omax):
        return (x - imin)*(omax - omin) / (imax - imin) + omin

    GPIO.setup(soilPwr, GPIO.OUTPUT)
    GPIO.output(soilPwr, GPIO.LOW)
    
    spi = spidev.SpiDev()
    spi.open(0, 0)

    try:
        while (True):
            # read soil moisture data
            if (read):
                soil_lock.acquire()
                try:
                    GPIO.output(soilPwr, GPIO.HIGH)
                    data = readADC(soil_adc)
                    if (data == -1):
                        print("Error Reading Soil!\n")
                    else:
                        # data = mapRange(data,
                        #                 config.imin, config.imax,
                        #                 config.omin, config.omax)
                        print("Moisture={0:0.1f}".format(data))
                        yp_soil.append(data)
                finally:
                    soil_lock.release()

            GPIO.output(soilPwr, GPIO.LOW)
            time.sleep(300000) # wait 5 minutes
    except KeyboardInterrupt:
        print("Ctrl-C pressed, from Soil!")
    finally:
        spi.close()
        GPIO.cleanup(soilPwr)
        print("Soil closed!")

def readADC(chan):
    # read ADC data
    # mostly taken from:
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
    return datum

def animate(i):
    soil_lock.acquire()
    try:
        ax1.clear()
        ax1.plot(xp_soil, yp_soil)
    finally:
        soil_lock.release()

    dht_lock.acquire()
    try:
        ax2.clear()
        ax2.plot(xp_temp, yp_temp)

        ax3.clear()
        ax3.plot(xp_humid, yp_humid)
    finally:
        dht_lock.release

if __name__ == "__main__":
    GPIO.setmode(GPIO.BOARD)

    soil_id = Thread(name="Soil", target=readSoilMoisture)
    dht_id = Thread(name="DHT11", target=readDHT)

    soil_id.start()
    dht_id.start()

    scene = animation.FuncAnimation(fig, animate, interval=300000)
    plot.show()

    soil_id.join()
    dht_id.join()
    return
