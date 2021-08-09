import paho.mqtt.client as mqtt
import json

# listens for messages from canaries, does something with them when they arrive
# basically just copy/pasted from the first example on
# https://www.eclipse.org/paho/index.php?page=clients/python/docs/index.php#usage-and-api


broker_address = "127.0.0.1"
broker_port = 8883

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe([("msr/84CCA8842F45", 1), ("msr/E8DB8496A0F6", 1), ("msr/9C9C1F458F3A", 1), ("msr/9C9C1F45B1E3", 1)])


# the callback for when a PUBLISH message is received from server
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    data = json.loads(msg.payload)
    print(data)
    print(data['temperature'])


client = mqtt.Client("P1")  # P1 is a unique identifier
client.on_connect = on_connect
client.on_message = on_message

client.username_pw_set("canary", "measuretemp")
client.connect(broker_address, broker_port)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.

client.loop_forever()


