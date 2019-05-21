# micropython-max7219
**MicroPython driver for MAX7219 with 7-segment modules**

* Utilizes hardware SPI, with user specified CS line.
* Supports cascading MAX7219 devices
* Number of digits per MAX7219 device can be specified

## ESP32 Examples

```python
import max7219
display = max7219.SevenSegment(digits=4, cs=0, scan_digits=6)
display.text("ABCDEF")
display.number(3.14159)
display.message("Hello World")
display.clear()
```

## Connections

ESP32            | max7219 LED Driver
---------------- | ----------------------
5V               | VCC 
GND              | GND
D7 MOSI          | DIN
D3 CS            | CS
D5 SCK           | CLK

## Links

* Based on [rm-hull's max7219.py (pre-2017 version)](https://github.com/rm-hull/max7219)
* [micropython.org](http://micropython.org)

## License

Licensed under the [MIT License](http://opensource.org/licenses/MIT).
