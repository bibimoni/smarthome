from homebit3_dht20 import DHT20
from homebit3_lcd1602 import LCD1602
from yolobit import *
from aiot_rgbled import RGBLed
import time
import urequests
import network

# ===== WIFI SETUP =====
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect("OPPO A78", "373152361")

while not wifi.isconnected():
    pass

# ===== INIT SENSORS =====
dht20 = DHT20()
lcd1602 = LCD1602()
rgb_led = RGBLed(pin2.pin, 4)

last_send = 0
fan_state = "OFF"
led_state = "OFF"

SERVER = "http://10.151.50.207:5000"

# ===== MAIN LOOP =====
while True:

    # ===== GET COMMAND FROM SERVER =====
    try:
        response = urequests.get(SERVER + "/api/get-commands")

        if response.status_code == 200:
            data = response.json()
            cmd = data.get("command", "")

            if cmd == "FAN_ON":
                pin1.write_digital(1)
                fan_state = "ON"

            elif cmd == "FAN_OFF":
                pin1.write_digital(0)
                fan_state = "OFF"

            elif cmd == "LED_ON":
                rgb_led.show(1, hex_to_rgb("#00ff00"))
                led_state = "ON"

            elif cmd == "LED_OFF":
                rgb_led.show(1, hex_to_rgb("#000000"))
                led_state = "OFF"

        response.close()

    except:
        pass

    # ===== SEND SENSOR EVERY 4 SECONDS =====
    if time.time() - last_send >= 4:
        last_send = time.time()

        dht20.read_dht20()
        temp  = dht20.dht20_temperature()
        humi  = dht20.dht20_humidity()
        light = round(translate(pin0.read_analog(), 0, 4095, 0, 100))

        # LCD display
        lcd1602.clear()
        lcd1602.move_to(0, 0)
        lcd1602.putstr('T:' + str(temp) + 'C')

        lcd1602.move_to(8, 0)
        lcd1602.putstr('H:' + str(humi) + '%')

        lcd1602.move_to(0, 1)
        lcd1602.putstr('L:' + str(light) + '%')

        # Serial output
        print(
            "T:" + str(temp) +
            ",H:" + str(humi) +
            ",L:" + str(light) +
            ",FAN:" + fan_state +
            ",LED:" + led_state
        )

        # Send to server
        try:
            res = urequests.post(
                SERVER + "/update",
                json={
                    "temp": temp,
                    "humi": humi,
                    "light": light
                }
            )
            res.close()
        except:
            pass

    time.sleep_ms(200)