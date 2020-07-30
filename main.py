# # esp-rak811-presion-temperatura-luminosidad
# #### Ing. Germán A. Xander 2020
#
# A simple example for educational purpose.
#
# * Using a esp32 as host to drive a rak811 via UART.
# * It uses the digital ambient light sensor BH1750 to measure the environment lighting.
# * the BMP180 Barometric Pressure/Temperature sensor.
# * the HYT271 Digital Humidity and Temperature sensor.
#
# Then send the reading from all three sensors as bytes to use the least possible payload.

from machine import UART, Pin, I2C
import time, binascii
from bh1750 import BH1750
from bmp180 import BMP180

reset=Pin(23, Pin.OUT)
led_onboard=Pin(2, Pin.OUT)

#define pins 4 and 5 for UART because UART0 are used for USB and
# UART1  are "used by Flash chip and cannot be used for other purposes."*
#* https://forum.micropython.org/viewtopic.php?p=27259&sid=5ffaee5b5c0819cefc11f73e91b804aa#p27259
i2c = I2C(0)
i2c = I2C(1, scl=Pin(5), sda=Pin(4))
s = BH1750(i2c)
bmp180 = BMP180(i2c)
bmp180.oversample_sett = 2

def pisca(tiempo):
  led_onboard.on()
  time.sleep(tiempo)
  led_onboard.off()
  time.sleep(tiempo)
  led_onboard.on()
  time.sleep(tiempo)
  led_onboard.off()
  time.sleep(tiempo)


x = 1
while True:
    uart=UART(1)
    print(x)
    if (uart or x==5):  #el puerto uart0 se usa para USB
        break
    x += 1
    time.sleep(1)
uart.init(115200, bits=8, parity=None, stop=1, rx=14, tx=12)
print(uart)
time.sleep(1)

reset.off()
time.sleep(1)
reset.on()
time.sleep(1)
print(str(uart.read()))

#Join as OTAA
#sleeps are to struggling with variable latencies
print("\n\njoin mode :")
uart.write(str.encode("at+set_config=lora:join_mode:0\r\n"))
time.sleep(3)
print(str(uart.read()))
print("\ndev_eui :")
uart.write(str.encode("at+set_config=lora:dev_eui:XXXX\r\n"))
time.sleep(3)
print(str(uart.read()))
print("\napp_eui :")
uart.write(str.encode("at+set_config=lora:app_eui:XXXX\r\n"))
time.sleep(3)
print(str(uart.read()))
print("\napp_key :")
uart.write(str.encode("at+set_config=lora:app_key:XXXX\r\n"))
time.sleep(3)
print(str(uart.read()))
print("\nDR 3 :")
uart.write(str.encode("at+set_config=lora:dr:3\r\n"))
time.sleep(3)
print(str(uart.read()))

print("\njoin :")

i=0
retorno="None"
print("conectando OTAA")
while (i<5 and retorno.find("OK")==-1):
    uart.write(str.encode("at+join\r\n"))
    time.sleep(5)
    retorno=str(uart.read())
    time.sleep(5)
    retorno=str(uart.read())
    print("intento OTAA: " + str(i) +"  "+ retorno)
    i += 1

while True:
    uart.write(str.encode("at+set_config=device:sleep:0\r\n")) #wake up rak811
    time.sleep(2)
    print("wake-up: "+str(uart.read()))
    lighting=s.luminance(BH1750.ONCE_HIRES_2) #I modified bh1750 lib a little bit. Now it returns 2 bytes
    #payload=binascii.hexlify("AB")
    pressure=(bmp180.pressure/100)-850 # I don't expect pressure below 850 hPa, so a index te value. This way I can send only one byte
    temperature=bmp180.temperature
    i2c.writeto(40, b'123')
    hyt271=i2c.readfrom(40, 4)
    # humidity = ((reading[0] & 0x3F) * 0x100 + reading[1]) * (100.0 / 16383.0)
    # temperature = 165.0 / 16383.0 * ((reading[2] * 0x100 + (reading[3] & 0xFC)) >> 2) - 40

    #send payload as bytes
    payload=binascii.hexlify(bytes([lighting[0],
                                    lighting[1],int(temperature),
                                    int((temperature-int(temperature))*100),
                                    int(pressure),int((pressure-int(pressure))*100),
                                    hyt271[0],
                                    hyt271[1],
                                    hyt271[2],
                                    hyt271[3]]))
    print("enviando payload: "+ str(payload))
    # print((lighting[0]<<8 | lighting[1]) / (1.2))
    uart.write(str.encode("at+send=lora:1,:") + payload +str.encode("\r\n"))
    time.sleep(5)
    resultado=str(uart.read())
    print(resultado)
    if (resultado.find("OK")>=0):
        time.sleep(1)
        print("recibido: " + str(uart.read()))
        uart.write(str.encode("at+get_config=lora:status\r\n"))
        time.sleep(1)
        estado=uart.read()
        contador=int(str(estado).split("\\r\\nDownLinkCounter")[0].split("UpLinkCounter: ")[1])-1#retrive lora counter
        print("Frame Nro: "+ str(contador))
        pisca(.25)
    uart.write(str.encode("at+set_config=device:sleep:1\r\n")) #put rak811 in sleep mode
    time.sleep(1)
    print("sleep: "+str(uart.read()))
    i +=1
    #int(payload[0]<<16) + int(payload[1]<<8) + int(payload[2])
    time.sleep(170)
