import can
import spidev
import time

# Initialize SPI
spi = spidev.SpiDev()
spi.open(0, 0)  # Open SPI bus 0, device (CS) 0
spi.max_speed_hz = 1000000  # Set SPI speed to 1 MHz

# MCP2515 initialization sequence
def mcp2515_init():
    # Reset MCP2515
    spi.xfer2([0xC0])
    time.sleep(0.1)
    
    # Set configuration mode
    spi.xfer2([0x02, 0x0F, 0x80])
    
    # Set bit timing
    spi.xfer2([0x02, 0x29, 0x41])
    spi.xfer2([0x02, 0x28, 0x00])
    spi.xfer2([0x02, 0x2A, 0x03])
    
    # Enable interrupts
    spi.xfer2([0x02, 0x2B, 0x03])
    
    # Set normal mode
    spi.xfer2([0x02, 0x0F, 0x00])

# Initialize MCP2515
mcp2515_init()

# Create a CAN bus instance
bus = can.interface.Bus(channel='vcan0', bustype='socketcan')

# Send a CAN message
msg = can.Message(arbitration_id=0x123, data=[0x11, 0x22, 0x33, 0x44, 0x55, 0x66, 0x77, 0x88], extended_id=False)
bus.send(msg)

print("Message sent on CAN bus")

# Receive a CAN message
while True:
    message = bus.recv(1.0)  # Timeout in seconds
    if message:
        print(f"Received message: {message}")