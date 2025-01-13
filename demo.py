import spidev
import time

# Initialize SPI
spi = spidev.SpiDev()
spi.open(0, 1)  # Open SPI bus 0, device (CS) 1
spi.max_speed_hz = 1000000  # Set SPI speed to 1 MHz

# MCP2515 register addresses
TXB0CTRL = 0x30
TXB0SIDH = 0x31
TXB0D0 = 0x36
RXB0CTRL = 0x60
RXB0SIDH = 0x61
RXB0D0 = 0x66
CANINTF = 0x2C

# MCP2515 commands
WRITE = 0x02
READ = 0x03
BIT_MODIFY = 0x05
LOAD_TX_BUFFER = 0x40
RTS_TX0 = 0x81
READ_RX_BUFFER = 0x90
RESET = 0xC0

# MCP2515 initialization sequence
def mcp2515_init():
    # Reset MCP2515
    spi.xfer2([RESET])
    time.sleep(0.1)
    
    # Set configuration mode
    spi.xfer2([WRITE, 0x0F, 0x80])
    
    # Set bit timing
    spi.xfer2([WRITE, 0x29, 0x41])
    spi.xfer2([WRITE, 0x28, 0x00])
    spi.xfer2([WRITE, 0x2A, 0x03])
    
    # Enable interrupts
    spi.xfer2([WRITE, 0x2B, 0x03])
    
    # Set normal mode
    spi.xfer2([WRITE, 0x0F, 0x00])

# Send a CAN message
def send_can_message(id, data):
    # Set TX buffer ID
    spi.xfer2([WRITE, TXB0SIDH, (id >> 3) & 0xFF, (id << 5) & 0xE0])
    
    # Set TX buffer data length and data
    spi.xfer2([WRITE, TXB0D0, len(data)] + data)
    
    # Request to send message
    spi.xfer2([RTS_TX0])

# Receive a CAN message
def receive_can_message():
    # Check if a message is received
    status = spi.xfer2([READ, CANINTF, 0x00])[2]
    if status & 0x01:
        # Read received message ID
        id_high = spi.xfer2([READ, RXB0SIDH, 0x00])[2]
        id_low = spi.xfer2([READ, RXB0SIDH + 1, 0x00])[2]
        id = (id_high << 3) | (id_low >> 5)
        
        # Read received message data length
        length = spi.xfer2([READ, RXB0D0 - 1, 0x00])[2] & 0x0F
        
        # Read received message data
        data = spi.xfer2([READ_RX_BUFFER, RXB0D0] + [0x00] * length)[1:]
        
        # Clear receive flag
        spi.xfer2([BIT_MODIFY, CANINTF, 0x01, 0x00])
        
        return id, data
    return None, None

# Initialize MCP2515
mcp2515_init()

while True:
    for i in range(0x00, 0xFFF):
        send_can_message(i, [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
    print("Message sent on CAN bus")

# while True:
#     # Send a CAN message
#     send_can_message(0x2FF, [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF])
#     print("Message sent on CAN bus")
#     time.sleep(1)

# # Receive a CAN message
# while True:
#     id, data = receive_can_message()
#     if id is not None:
#         print(f"Received message: ID={id}, Data={data}")
#     time.sleep(1)