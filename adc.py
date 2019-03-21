# mostly taken from https://github.com/pimylifeup/Pi-ADC-Example-Code
# but made more special

import spidev
import time

delay = 0.5
soil = 0 # soil moisture sensor on channel 0 of ADC

spi = spidev.SpiDev()
spi.open(0, 0)

try:
  while (True):
    # read from ADC until Ctrl+C
    readADC(soil)
    time.delay(0.5)
except KeyboardInterrupt:
  spi.close()


def readADC(chan):
  if ((chan > 7) or (chan < 0)):
    return -1
  
  # from MCP3008 datasheet:
  # Configure bits for channel
  # 1 is the Start Bit
  # 0x1000 + chan << 4 are the Configure Bits
  # 0 is read as dont cares
  # See Section 6.1 for more info
  data = spi.xfer2([1, (0x1000 + chan) << 4, 0])
  #data = ((data[1] & 0x11) << 8) + data[2]
  return data
