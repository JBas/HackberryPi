import Adafruit_DHT
import config

sensor = Adafruit_DHT.DHT11

try:
    while (True):
        humidity, temperature = Adafruit.DHT.read_retry(sensor, config.temp)
    
        if ((humidity is not None) and (temperature is not None)):
            print("Temp={0:0.1f}*, Humidity={1:0.1f}%".format(temperature, humidity))
        else:
            print("Error!\n");
        time.sleep(300000) # wait for 5 minutes
except KeyboardInterrupt:
    return
