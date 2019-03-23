import spidev
import time
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import Adafruit_DHT


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
            print("{0}\n".format(main.readADC(main.soil_adc)))
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
        humidity, temperature = Adafruit_DHT.read_retry(11, 17)
        print("Temp: {0:0.1f} C  Humidity: {1:0.1f} %".format(temperature, humidity)
    return

testDHT()



