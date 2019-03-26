from threading import Thread, Lock
import spidev
import time
import json
import RPi.GPIO as GPIO
import sensors
import plotter

BTN_PWR = 25
BTN_WATER = 24
ON = True
MOTOR_OFF = False

lock = Lock()

class WorkerThread(Thread):
    def __init__(self, p):
        Thread.__init__(self)
        self.data = {}
        self.data["humid"] = []
        self.data["temp"] = []
        self.data["soil"] = []

        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)

        self.p = p
        
        return

    def saveData(self, filename):
        lock.acquire()
        with open(filename, "w") as file:
            json.dump(self.data, file)
        lock.release()
        return

    def run(self):
        try:
            while (ON):
                sensors.readDHT(self.data)
                sensors.readSoilMoisture(self.data, self.spi)

                moist = self.data["soil"][-1]
                if ((moist["M"] < 10) and (not MOTOR_OFF)):
                    print("TIME TO WATER!")
                    sensors.pumpWater(self.p)

                if (len(self.data["humid"]) == 101):
                    self.data["humid"].pop(0)
                if (len(self.data["temp"]) == 101):
                    self.data["temp"].pop(0)
                if (len(self.data["soil"]) == 101):
                    self.data["soil"].pop(0)
                self.saveData("data.json")
                time.sleep(2)
        #except:
        #    print("Exception!")
        finally:
            self.spi.close()
        return # on return, kills thread


def btnMode(i):
    global ON
    global MOTOR_OFF
    if (MOTOR_OFF):
        print("Received shutdown signal...")
        ON = False
    else:
        print("Turning off motor...")
        MOTOR_OFF = True
    return

def manualWater(i):
    global MOTOR_OFF
    if (MOTOR_OFF):
        print("Turning on motor...")
        MOTOR_OFF = False
    else:
        sensors.pumpWater(None)
    return


def main():
    GPIO.setmode(GPIO.BCM)
    #GPIO.setwarnings(False)

    GPIO.setup(sensors.SOIL_PWR, GPIO.OUT)
    GPIO.output(sensors.SOIL_PWR, GPIO.LOW)
    GPIO.setup(sensors.MOTOR_PWM, GPIO.OUT)
    GPIO.output(sensors.MOTOR_PWM, GPIO.LOW)
    #p = GPIO.PWM(sensors.MOTOR_PWM, 1)
    #p.start(0)

    GPIO.setup(BTN_PWR, GPIO.IN,
               pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(BTN_PWR, GPIO.FALLING,
                          callback=btnMode,
                          bouncetime=200)
    GPIO.setup(BTN_WATER, GPIO.IN,
               pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(BTN_WATER, GPIO.FALLING,
                          callback=manualWater,
                          bouncetime=200)

    worker = WorkerThread(None)
    worker.setName("Worker")

    worker.start()
    plotter.plotter(lock)
    worker.join()

    plotter.endPlotter()
    #p.stop()
    GPIO.cleanup()
    return


if __name__ == "__main__":
    main()
