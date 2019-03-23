from threading import Thread, Lock
import time
import datetime as dt
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
fig = plt.figure()
ax1 = fig.add_subplot(3, 1, 1)
ax2 = fig.add_subplot(3, 1, 2)
ax3 = fig.add_subplot(3, 1, 3)

#--------------------Thread Functions--------------------#

def readDHT(xp_humid, yp_humid, xp_temp, yp_temp):
    try:
        while (True):
            # read temp/humid data
            if (dht_lock.acquire()):
                try:
                    humidity, temperature = DHT.read_retry(DHT.DHT11, dht_sig)
                    if ((humidity is not None) and (temperature is not None)):
                        print("Temp={0:0.1f}*, Humidity={0:0.1f}%\n".format(temperature, humidity))
                        t = dt.datetime.now().strftime("%H:%M")
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
                finally:
                    dht_lock.release()
                time.sleep(5) # wait 5 minutes
            else:
                print("Lock NOT Acquired!\n")
    except KeyboardInterrupt:
        print("Ctrl-C pressed, from DHT!\n")
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
                    data = readADC(soil_adc, spi)
                    if (data == -1):
                        print("Error Reading Soil!\n")
                    else:
                        # data = mapRange(data,
                        #                 config.imin, config.imax,
                        #                 config.omin, config.omax)
                        print("Moisture={0:0.1f}".format(data))
                        yp_soil.append(data)
                        yp_soil = yp_soil[-100:]

                        t = dt.datetime.now().strftime("%H:%M")
                        xp_soil.append(t)
                        xp_soil = xp_soil[-100:]
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

def readADC(chan, spi):
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
    datum = ((datum[1] & 0x11) << 8) + datum[2]
    return datum

def animate(i, xp_humid, yp_humid, xp_temp, yp_temp):
    #soil_lock.acquire()
    #try:
    #    ax1.clear()
    #    ax1.plot(xp_soil, yp_soil)
    #    ax1.set_title("Soil Moisture v Time")
    #finally:
    #    soil_lock.release()

    if (True):#dht_lock.acquire()):
        #try:
        print(yp_humid)
        ax2.clear()
        ax2.plot(xp_temp, yp_temp)
        ax2.set_title("Temperature v Time")

        ax3.clear()
        ax3.plot(xp_humid, yp_humid)
        ax3.set_title("Humidity v Time")
        #finally:
        #    dht_lock.release
    else:
        print("Lock NOT Acquired!\n")

def main():
    GPIO.setmode(GPIO.BOARD)

    #soil_id = Thread(name="Soil", target=readSoilMoisture)
    dht_id = Thread(name="DHT11", target=readDHT,
                    args=(xp_humid, yp_humid,
                          xp_temp, yp_temp))

    #soil_id.start()
    dht_id.start()

    scene = animation.FuncAnimation(fig, animate, interval=1000,
                                    fargs=(xp_humid, yp_humid,
                                           xp_temp, yp_temp))
    plt.show()

    #soil_id.join()
    dht_id.join()
    return

if __name__ == "__main__":
    main()
