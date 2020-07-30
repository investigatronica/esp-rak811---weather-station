# esp-rak811-presion-temperatura-luminosidad
#### Ing. Germán A. Xander 2020

A simple example for educational purpose.

* Using a esp32 as host to drive a rak811 via UART.
* It uses the digital ambient light sensor BH1750 to measure the environment lighting.
* the BMP180 Barometric Pressure/Temperature sensor.
* the HYT271 Digital Humidity and Temperature sensor.

Then send the reading from all three sensors as bytes to use the least possible payload.
