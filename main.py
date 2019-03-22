from threading import Thread
import time
import RPi.GPIO as GPIO
import spidev
import Adafruit_DHT as DHT
import config

def readDHT():
    try:
        sensor = DHT.DHT11
        while (True):
            # read temp/humid data
            humidity, temperature = DHT.read_retry(sensor, config.temp)

            if ((humidity is not None) and (temperature is not None)):
                print("Temp={0:0.1f}*, Humidity={0:0.1f}%\n".format(temperature, humidity))
            else:
                print("Error Reading DHT!\n")
            time.sleep(300000) # wait 5 minutes
            i = 1/0
    except KeyboardInterrupt:
        print("Ctrl-C pressed, from DHT!\n")
    except ZeroDivisionError:
        print("Divided by 0, from DHT!\n")
    finally:
        print("DHT closed!\n")
        

def readSoilMoisture():
    GPIO.setup(config.soilPwr, GPIO.OUTPUT)
    
    spi = spidev.SpiDev()
    spi.open(0, 0)

    try:
        while (True):
            # read soil moisture data
            if (config.read):
                GPIO.output(config.soilPwr, GPIO.HIGH)
                print(readADC(config.soilSig))

            GPIO.output(config.soilPwr, GPIO.LOW)
            time.sleep(300000) # wait 5 minutes
    except KeyboardInterrupt:
        print("Ctrl-C pressed, from Soil!")
    finally:
        spi.close()
        GPIO.cleanup(config.soilPwr)
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

if __name__ == "__main__":
    GPIO.setmode(GPIO.BOARD)

    soil_id = Thread(name="Soil", target=readSoilMoisture)
    dht_id = Thread(name="DHT11", target=readDHT)
    soil_id.start()
    dht_id.start()

    soil_id.join()
    dht_id.join()
