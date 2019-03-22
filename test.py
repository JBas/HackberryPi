import main

while (True):
    try:
        print("{0}\n".format(main.readADC(main.soil_adc)))
    except KeyboardInterrupt:
        print("Closing!\n")


