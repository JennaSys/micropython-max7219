from machine import Pin, SPI
import time

from seven_segment_ascii import get_char2


MAX7219_DIGITS = 8

MAX7219_REG_NOOP = 0x0
MAX7219_REG_DIGIT0 = 0x1
MAX7219_REG_DIGIT1 = 0x2
MAX7219_REG_DIGIT2 = 0x3
MAX7219_REG_DIGIT3 = 0x4
MAX7219_REG_DIGIT4 = 0x5
MAX7219_REG_DIGIT5 = 0x6
MAX7219_REG_DIGIT6 = 0x7
MAX7219_REG_DIGIT7 = 0x8
MAX7219_REG_DECODEMODE = 0x9
MAX7219_REG_INTENSITY = 0xA
MAX7219_REG_SCANLIMIT = 0xB
MAX7219_REG_SHUTDOWN = 0xC
MAX7219_REG_DISPLAYTEST = 0xF

SPI_BUS = 1  # hardware SPI
SPI_BAUDRATE = 100000
SPI_CS = 0    # D3


class SevenSegment:
    def __init__(self, digits=8, scan_digits=MAX7219_DIGITS, baudrate=SPI_BAUDRATE, cs=SPI_CS, reverse=False):
        """
        Constructor:
        `digits` should be the total number of individual digits being displayed
        `cs` is the GPIO port to use for the chip select line of the SPI bus - defaults to GPIO 0 / D3
        `scan_digits` is the number of digits each individual max7219 displays
        `baudrate` defaults to 100KHz, note that excessive rates may result in instability (and is probably unnecessary)
        `reverse` is a flag for some boards that have displays wired differently
        """

        self.digits = digits
        self.devices = -(-digits // scan_digits)  # ceiling integer division
        self.scan_digits = scan_digits
        self._buffer = [0] * digits
        self._spi = SPI(SPI_BUS, baudrate=baudrate, polarity=0, phase=0)
        self._cs = Pin(cs, Pin.OUT, value=1)
        self.reverse = reverse

        self.command(MAX7219_REG_SCANLIMIT, scan_digits-1)    # digits to display on each device  0-7
        self.command(MAX7219_REG_DECODEMODE, 0)   # use segments (not digits)
        self.command(MAX7219_REG_DISPLAYTEST, 0)  # no display test
        self.command(MAX7219_REG_SHUTDOWN, 1)     # not blanking mode
        self.brightness(7)                        # intensity: range: 0..15
        self.clear()

    def command(self, register, data):
        """Sets a specific register some data, replicated for all cascaded devices."""
        self._write([register, data] * self.devices)

    def _write(self, data):
        """Send the bytes (which should comprise of alternating command, data values) over the SPI device."""
        self._cs.off()
        self._spi.write(bytes(data))
        self._cs.on()

    def clear(self, flush=True):
        """Clears the buffer and if specified, flushes the display."""
        self._buffer = [0] * self.digits
        if flush:
            self.flush()

    def flush(self):
        # Check reverse flag
        if (self.reverse):
            """For each digit, cascade out the contents of the reversed buffer cells to the SPI device backwards."""
            for dev in range(self.devices):
                for pos in reversed(range(self.scan_digits)): # reverse read data in buffer and write to display backwards
                    self._write([pos + MAX7219_REG_DIGIT0, self._buffer[((self.scan_digits - 1) - pos) + (dev * self.scan_digits)]] + ([MAX7219_REG_NOOP, 0] * dev))
        else:
            """For each digit, cascade out the contents of the buffer cells to the SPI device."""
            for dev in range(self.devices):
                for pos in range(self.scan_digits):
                    self._write([pos + MAX7219_REG_DIGIT0, self._buffer[pos + (dev * self.scan_digits)]] + ([MAX7219_REG_NOOP, 0] * dev))

    def brightness(self, intensity):
        """Sets the brightness level of all cascaded devices to the same intensity level, ranging from 0..15."""
        self.command(MAX7219_REG_INTENSITY, intensity)

    def letter(self, position, char, dot=False, flush=True):
        """Looks up the appropriate character representation for char and updates the buffer, flushes by default."""
        value = get_char2(char) | (dot << 7)
        self._buffer[position] = value

        if flush:
            self.flush()

    def text(self, text):
        """Outputs the text (as near as possible) on the specific device."""
        self.clear(False)
        text = text[:self.digits]  # make sure we don't overrun the buffer
        for pos, char in enumerate(text):
            self.letter(pos, char, flush=False)

        self.flush()

    def number(self, val):
        """Formats the value according to the parameters supplied, and displays it."""
        self.clear(False)
        strval = ''
        if isinstance(val, (int, float)):
            strval = str(val)
        elif isinstance(val, str):
            if val.replace('.', '', 1).strip().isdigit():
                strval = val

        if '.' in strval:
            strval = strval[:self.digits+1]
        else:
            strval = strval[:self.digits]

        pos = 0
        for char in strval:
            dot = False
            if char == '.':
                continue
            else:
                if pos < len(strval) - 1:
                    if strval[pos + 1] == '.':
                        dot = True
                self.letter(pos, char, dot, False)
                pos += 1

        self.flush()

    def scroll(self, rotate=True, reverse=False, flush=True):
        """Shifts buffer contents left or right (reverse), with option to wrap around (rotate)."""
        if reverse:
            tmp = self._buffer.pop()
            if rotate:
                self._buffer.insert(0, tmp)
            else:
                self._buffer.insert(0, 0x00)
        else:
            tmp = self._buffer.pop(0)
            if rotate:
                self._buffer.append(tmp)
            else:
                self._buffer.append(0x00)

        if flush:
            self.flush()

    def message(self, text, delay=0.4):
        """Transitions the text message across the devices from left-to-right."""
        self.clear(False)
        for char in text:
            time.sleep(delay)
            self.scroll(rotate=False, flush=False)
            self.letter(self.digits-1, char)
