from threading import Lock
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import json

fig = plt.figure()
ax1 = fig.add_subplot(3, 1, 1)
ax2 = fig.add_subplot(3, 1, 2)
ax3 = fig.add_subplot(3, 1, 3)


def plotter(lock):
    ani = animation.FuncAnimation(fig, plotData, fargs=(lock, ), interval=2500)
    plt.show()
    return

def endPlotter():
    plt.close("all")
    return

def plotData(i, lock):
    humidity = []
    temperature = []
    moisture = []

    try:
        lock.acquire()
        with open("data.json") as file:
            data = json.load(file)

            for hum in data["humid"]:
                t = hum["t"]
                H = hum["H"]
                humidity.append((t, H))

            for temp in data["temp"]:
                t = temp["t"]
                T = temp["T"]
                temperature.append((t, T))

            for moist in data["soil"]:
                t = moist["t"]
                M = moist["M"]
                moisture.append((t, M))

        ax1.clear()
        ax1.plot(*zip(*humidity))
        ax1.set(xlabel="time", ylabel="%",
                title="Humidity v Time",
                xticklabels=[])

        ax2.clear()
        ax2.plot(*zip(*temperature))
        ax2.set(xlabel="time", ylabel="degrees C",
                title="Temperature v Time",
                xticklabels=[])

        ax3.clear()
        ax3.plot(*zip(*moisture))
        ax3.set(xlabel="time", ylabel="%",
                title="Soil Moisture v Time",
                xticklabels=[])
    except FileNotFoundError:
        print("WorkerThread still collecting!")
    finally:
        lock.release()
    return
