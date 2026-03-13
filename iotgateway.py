import paho.mqtt.client as mqtt
import random
import time

# ====== CONFIG ======
ADAFRUIT_AIO_USERNAME = "quanghung2405"
ADAFRUIT_AIO_KEY = "aio_aObH04xf0ktcNpDfZJOZrZIiFzf8"

BROKER = "io.adafruit.com"
PORT = 1883

# Feeds
TEMP_FEED = f"{ADAFRUIT_AIO_USERNAME}/feeds/temperature"
HUMID_FEED = f"{ADAFRUIT_AIO_USERNAME}/feeds/humid"
LIGHT_FEED = f"{ADAFRUIT_AIO_USERNAME}/feeds/light"
FAN_FEED = f"{ADAFRUIT_AIO_USERNAME}/feeds/fan"
LED_FEED = f"{ADAFRUIT_AIO_USERNAME}/feeds/led"


# ====== CALLBACK ======
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to Adafruit IO")
        client.subscribe(FAN_FEED)
        client.subscribe(LED_FEED)
    else:
        print("Connection failed")


def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    print("Received from", msg.topic, ":", payload)

    if msg.topic == FAN_FEED:
        if payload == "1":
            print("Fan ON")
        else:
            print("Fan OFF")

    if msg.topic == LED_FEED:
        if payload == "1":
            print("LED ON")
        else:
            print("LED OFF")


# ====== MQTT SETUP ======
client = mqtt.Client()
client.username_pw_set(ADAFRUIT_AIO_USERNAME, ADAFRUIT_AIO_KEY)

client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT, 60)
client.loop_start()

# ====== SIMULATE DATA ======
while True:
    temperature = random.randint(0, 40)
    humid = random.randint(0, 100)
    light = random.randint(0, 100)

    client.publish(TEMP_FEED, temperature)
    client.publish(HUMID_FEED, humid)
    client.publish(LIGHT_FEED, light)

    print("Sent: Temp =", temperature,
          "Humid =", humid,
          "Light =", light)

    time.sleep(10)
