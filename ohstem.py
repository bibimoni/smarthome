"""
YoloBit Firmware for YoloHome Smart Home System
Devices: DHT20, Light Sensor, Fan, RGB LED, LCD1602
"""

from homebit3_dht20 import DHT20
from homebit3_lcd1602 import LCD1602
from yolobit import *
import time
import network
import ujson
import umqtt.simple as mqtt

# Configuration
WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"
ADAFRUIT_IO_USERNAME = "quanghung2405"
ADAFRUIT_IO_KEY = "aio_anJO06oMkhLtJbAYhp4yRGMmoFoe"
DEVICE_LOCATION = "living-room"
READ_INTERVAL = 5

# Feed names
FEED_TEMP = f"{ADAFRUIT_IO_USERNAME}/feeds/temperature.{DEVICE_LOCATION}"
FEED_HUMIDITY = f"{ADAFRUIT_IO_USERNAME}/feeds/humidity.{DEVICE_LOCATION}"
FEED_LIGHT = f"{ADAFRUIT_IO_USERNAME}/feeds/light.{DEVICE_LOCATION}"
FEED_FAN = f"{ADAFRUIT_IO_USERNAME}/feeds/fan.{DEVICE_LOCATION}"
FEED_RGB = f"{ADAFRUIT_IO_USERNAME}/feeds/rgb.{DEVICE_LOCATION}"

# Global state
fan_speed = 0
rgb_color = "0,0,0"
last_send = 0
client = None

# Initialize sensors
dht20 = DHT20()
lcd1602 = LCD1602()

def connect_wifi():
    print(f"Connecting to WiFi: {WIFI_SSID}")
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.connect(WIFI_SSID, WIFI_PASSWORD)
    
    retry = 0
    while not wifi.isconnected() and retry < 20:
        print(".", end="")
        time.sleep(0.5)
        retry += 1
    
    if wifi.isconnected():
        print(f"\nWiFi connected! IP: {wifi.ifconfig()[0]}")
        return True
    print("\nWiFi connection failed!")
    return False

def on_message(topic, msg):
    global fan_speed, rgb_color
    
    topic_str = topic.decode('utf-8')
    value = msg.decode('utf-8')
    print(f"Received: {topic_str} = {value}")
    
    if 'fan' in topic_str:
        try:
            speed = max(0, min(100, int(value)))
            fan_speed = speed
            pin1.write_analog(int(speed * 1023 / 100))
            print(f"Fan speed: {speed}%")
        except ValueError:
            if value.upper() == 'ON':
                pin1.write_analog(1023)
                fan_speed = 100
                print("Fan: ON")
            else:
                pin1.write_analog(0)
                fan_speed = 0
                print("Fan: OFF")
    
    elif 'rgb' in topic_str:
        try:
            r, g, b = map(int, value.split(','))
            r, g, b = max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))
            np = neopixel.NeoPixel(pin2, 1)
            np[0] = (r, g, b)
            np.write()
            rgb_color = f"{r},{g},{b}"
            print(f"RGB: ({r}, {g}, {b})")
        except Exception as e:
            print(f"RGB error: {e}")

def connect_mqtt():
    global client
    try:
        client = mqtt.MQTTClient('yolobit', 'io.adafruit.com', 1883,
                                  ADAFRUIT_IO_USERNAME, ADAFRUIT_IO_KEY)
        client.set_callback(on_message)
        client.connect()
        client.subscribe(FEED_FAN)
        client.subscribe(FEED_RGB)
        print("Connected to Adafruit IO")
        return True
    except Exception as e:
        print(f"MQTT connection failed: {e}")
        return False

def read_sensors():
    dht20.read_dht20()
    temp = round(dht20.dht20_temperature(), 1)
    hum = round(dht20.dht20_humidity(), 1)
    light = round(pin0.read_analog() * 100 / 4095)
    return temp, hum, light

def update_lcd(temp, hum, light):
    lcd1602.clear()
    lcd1602.move_to(0, 0)
    lcd1602.putstr(f'T:{temp}C H:{hum}%')
    lcd1602.move_to(0, 1)
    lcd1602.putstr(f'L:{light}% F:{fan_speed}%')

def publish_sensors(temp, hum, light):
    if client is None:
        return
    try:
        client.publish(FEED_TEMP, str(temp))
        time.sleep(0.1)
        client.publish(FEED_HUMIDITY, str(hum))
        time.sleep(0.1)
        client.publish(FEED_LIGHT, str(light))
        time.sleep(0.1)
        print(f"Published: T={temp}C, H={hum}%, L={light}%")
    except Exception as e:
        print(f"Publish error: {e}")

def main():
    global last_send
    
    print("YoloHome - YoloBit Firmware")
    
    if not connect_wifi():
        print("Restarting...")
        time.sleep(5)
        import machine
        machine.reset()
    
    if not connect_mqtt():
        print("Restarting...")
        time.sleep(5)
        import machine
        machine.reset()
    
    print(f"Starting main loop (interval: {READ_INTERVAL}s)")
    
    while True:
        try:
            client.check_msg()
            
            if time.time() - last_send >= READ_INTERVAL:
                last_send = time.time()
                temp, hum, light = read_sensors()
                update_lcd(temp, hum, light)
                print(f"T:{temp}C, H:{hum}%, L:{light}%, FAN:{fan_speed}%")
                publish_sensors(temp, hum, light)
            
            time.sleep(0.1)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()
