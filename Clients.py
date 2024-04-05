#
# Copyright 2021 HiveMQ GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import time
import random
import threading

import paho.mqtt.client as paho
from paho import mqtt




# setting callbacks for different events to see if it works, print the message etc.
def on_connect(client, userdata, flags, rc, properties=None):
    """
        Prints the result of the connection with a reasoncode to stdout ( used as callback for connect )
        :param client: the client itself
        :param userdata: userdata is set when initiating the client, here it is userdata=None
        :param flags: these are response flags sent by the broker
        :param rc: stands for reasonCode, which is a code for the connection result
        :param properties: can be used in MQTTv5, but is optional
    """
    print("CONNACK received with code %s." % rc)




# with this callback you can see if your publish was successful
def on_publish(client, userdata, mid, properties=None):
    """
        Prints mid to stdout to reassure a successful publish ( used as callback for publish )
        :param client: the client itself
        :param userdata: userdata is set when initiating the client, here it is userdata=None
        :param mid: variable returned from the corresponding publish() call, to allow outgoing messages to be tracked
        :param properties: can be used in MQTTv5, but is optional
    """
    print("mid: " + str(mid))




# print which topic was subscribed to
def on_subscribe(client, userdata, mid, granted_qos, properties=None):
    """
        Prints a reassurance for successfully subscribing
        :param client: the client itself
        :param userdata: userdata is set when initiating the client, here it is userdata=None
        :param mid: variable returned from the corresponding publish() call, to allow outgoing messages to be tracked
        :param granted_qos: this is the qos that you declare when subscribing, use the same one for publishing
        :param properties: can be used in MQTTv5, but is optional
    """
    print("Subscribed: " + str(mid) + " " + str(granted_qos))




# print message, useful for checking if it was successful
def on_message(client, userdata, msg):
    """
        Prints a mqtt message to stdout ( used as callback for subscribe )
        :param client: the client itself
        :param userdata: userdata is set when initiating the client, here it is userdata=None
        :param msg: the message with topic and payload
    """
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))




# Function to publish random data to a topic
def publish_random_data(client, topic):
    data = random.randint(1, 100)
    client.publish(topic, payload=data, qos=1)
    print(f"Published to {topic}: {data}")




# using MQTT version 5 here, for 3.1.1: MQTTv311, 3.1: MQTTv31
# userdata is user defined data of any type, updated by user_data_set()
# client_id is the given name of the client
client1 = paho.Client(callback_api_version=paho.CallbackAPIVersion.VERSION1, client_id="", userdata=None, protocol=paho.MQTTv5)
client1.on_connect = on_connect

client2 = paho.Client(callback_api_version=paho.CallbackAPIVersion.VERSION1, client_id="", userdata=None, protocol=paho.MQTTv5)
client2.on_connect = on_connect

client3 = paho.Client(callback_api_version=paho.CallbackAPIVersion.VERSION1, client_id="", userdata=None, protocol=paho.MQTTv5)
client3.on_connect = on_connect


# enable TLS for secure connection
client1.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
client2.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
client3.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
# set username and password
client1.username_pw_set("Publisher1", "Techassignment1")
client2.username_pw_set("Publisher2", "Techassignment1")
client3.username_pw_set("subscriber1", "Techassignment1")
# connect to HiveMQ Cloud on port 8883 (default for MQTT)
client1.connect("4b067d263a0d430aba56e5c1480d8e8b.s1.eu.hivemq.cloud", 8883)
client2.connect("4b067d263a0d430aba56e5c1480d8e8b.s1.eu.hivemq.cloud", 8883)
client3.connect("4b067d263a0d430aba56e5c1480d8e8b.s1.eu.hivemq.cloud", 8883)


# setting callbacks, use separate functions like above for better visibility
client1.on_subscribe = on_subscribe
client1.on_message = on_message
client1.on_publish = on_publish

client2.on_subscribe = on_subscribe
client2.on_message = on_message
client2.on_publish = on_publish

client3.on_subscribe = on_subscribe
client3.on_message = on_message
client3.on_publish = on_publish

# subscribe to all topics of encyclopedia by using the wildcard "#"
client3.subscribe("encyclopedia/#", qos=1)


# create thread to run 2 loops at the same time
subscriber_loop_thread = threading.Thread(target=client3.loop_forever)
subscriber_loop_thread.start()


# Start publishing random data every 3 seconds
while True: 
    publish_random_data(client1, "encyclopedia/temperature")
    publish_random_data(client2, "encyclopedia/temperature")
    time.sleep(3)


# a single publish, this can also be done in loops, etc.
# client.publish("encyclopedia/temperature", payload="hot", qos=1)


# loop_forever for simplicity, here you need to stop the loop manually
# you can also use loop_start and loop_stop
# client.loop_forever()
