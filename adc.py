# mostly taken from https://github.com/pimylifeup/Pi-ADC-Example-Code
# but made more special

import spidev
import time
import config

delay = 0.5 # ms

spi = spidev.SpiDev()
spi.open(0, 0)

def readADC(chan):
    if ((chan > 7) or (chan < 0)):
        return -1
  
    # from MCP3008 datasheet:
    # Configure bits for channel
    # 1 is the Start Bit
    # 0x1000 + chan << 4 are the Configure Bits
    # 0 is read as dont cares
    # See Section 6.1 for more info
    datum = spi.xfer2([1, (0x1000 + chan) << 4, 0])
    #data = ((data[1] & 0x11) << 8) + data[2]
    return datum

try:
    while (True):
        while (read_adc):
            # read from ADC until Ctrl+C
            config.adc_done = False
            data = []
            for chan in config.adc_chan:
                data.append(readADC(chan))
            print(data)
            config.adc_done = True
            time.sleep(delay)
except KeyboardInterrupt:
    spi.close()
