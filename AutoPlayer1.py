import os
import json
import threading
from dotenv import load_dotenv

import paho.mqtt.client as paho
from paho import mqtt
import time
from collections import deque
import random

# O represents an unvisited tile
grid = [
        ["O", "O", "O", "O", "O", "O", "O", "O", "O", "O"],
        ["O", "O", "O", "O", "O", "O", "O", "O", "O", "O"],
        ["O", "O", "O", "O", "O", "O", "O", "O", "O", "O"],
        ["O", "O", "O", "O", "O", "O", "O", "O", "O", "O"],
        ["O", "O", "O", "O", "O", "O", "O", "O", "O", "O"],
        ["O", "O", "O", "O", "O", "O", "O", "O", "O", "O"],
        ["O", "O", "O", "O", "O", "O", "O", "O", "O", "O"],
        ["O", "O", "O", "O", "O", "O", "O", "O", "O", "O"],
        ["O", "O", "O", "O", "O", "O", "O", "O", "O", "O"],
        ["O", "O", "O", "O", "O", "O", "O", "O", "O", "O"],
    ]

def bfs(grid, start, find_unvisited_tile = False):
    rows, cols = len(grid), len(grid[0])
    queue = deque([(start, [])])  
    visited = set()
    visited.add(start)
    
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # Right, left, down, up

    while queue:
        (current_y, current_x), path = queue.popleft()

        # Check for coin at the current location (ignore the starting point)
        if grid[current_y][current_x] == 'C' and (current_y, current_x) != start:
            return path + [(current_y, current_x)]
        
        # in the case that no coins are visible, instead look for an unvisited tile
        if find_unvisited_tile:
            if grid[current_y][current_x] == 'O' and (current_y, current_x) != start:
                return path + [(current_y, current_x)]

        # Explore neighbors
        for dy, dx in directions:
            ny, nx = current_y + dy, current_x + dx
            if 0 <= ny < rows and 0 <= nx < cols and (ny, nx) not in visited:
                # avoid either walls or other players
                if grid[ny][nx] != 'W' or 'Player' in grid[ny][nx]:
                    visited.add((ny, nx))
                    queue.append(((ny, nx), path + [(ny, nx)]))

    return None  # No path found

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
    if "game_state" in msg.topic:
        time.sleep(1)
        print("Recieving message...")
        suggest_next_move(msg.payload)
    
    if "scores" in msg.topic:
        print("message: " + msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

def suggest_next_move(payload):
    json_string = payload.decode('utf-8')

    # turn json string into python data format
    data = json.loads(json_string)

    current_postion = data['currentPosition']

    walls = data['walls']

    coin_1 = data['coin1']
    coin_2 = data['coin2']
    coin_3 = data['coin3']
    
    #visibility square

    # top left must fall within [0,0] corner of map
    top_left = [max(current_postion[0] - 2, 0), max(current_postion[1] - 2, 0)]

    # top right must fall within [0,9] corner of map
    top_right = [max(current_postion[0] - 2, 0), min(current_postion[1] + 2, 9)]

    # bottom left must fall within [9, 0] corner of map
    bottom_left = [min(current_postion[0] + 2, 9), max(current_postion[1] - 2, 0)]

    # bottom right must fall within [9, 9] corner of map
    bottom_right = [min(current_postion[0] + 2, 9), min(current_postion[1] + 2, 9)]

    #creating list with all coins in visiblity
    coins_in_visibility = []
    for coin_list in [coin_1, coin_2, coin_3]:
        for coin in coin_list:
            coins_in_visibility.append(coin)
    # for every tile in visiblity if not in coins_to_search then add to seen set
    for y in range(top_left[0], bottom_left[0] + 1):
        for x in range(top_left[1], top_right[1] + 1):
            if [y,x] == current_postion:
                # P represents player position
                grid[y][x] = "P"
            elif [y,x] in walls:
                # W represents a wall
                grid[y][x] = "W";
            elif [y,x] in coins_in_visibility:
                # C represents a coin of any value
                grid[y][x] = "C";
            else: 
                # X represents a tile has been visited
                grid[y][x] = "X";

    for row in grid:
        print(row)
    path = bfs(grid, (current_postion[0], current_postion[1]))
    print("Path to Nearest Coin: ", path)
    next_move = []
    if path: 
        next_move = path[0]
    else: 
        path = bfs(grid, (current_postion[0], current_postion[1]), True)
        if path: 
            next_move = path[0]
        else: 
            print("No more unvisited tiles possible")
            # client.publish(f"games/{lobby_name}/start", "STOP")

    # determining what direction to move based on the path retrieved from BFS
    if next_move[0] == current_postion[0]: 
        # if vertical position doesn't change move is horizontal
        if next_move[1] > current_postion[1]:
            #if x is larger then move to right direction
            client.publish(f"games/{lobby_name}/{player}/move", "RIGHT")
        else:
            client.publish(f"games/{lobby_name}/{player}/move", "LEFT")
    else:
        #if vertical position has changed then move is vertical
        if next_move[0] > current_postion[0]:
            #if y is greater then move in down direction (0,0 is top right corner )
            client.publish(f"games/{lobby_name}/{player}/move", "DOWN")
        else: 
            client.publish(f"games/{lobby_name}/{player}/move", "UP")
 
        #client.publish(f"games/{lobby_name}/{player}/move", random.choice(["LEFT", "RIGHT", "UP", "DOWN"]))

        

            
if __name__ == '__main__':
    load_dotenv(dotenv_path='./credentials.env')
    
    broker_address = os.environ.get('BROKER_ADDRESS')
    broker_port = int(os.environ.get('BROKER_PORT'))
    username = os.environ.get('USER_NAME')
    password = os.environ.get('PASSWORD')

    client = paho.Client(callback_api_version=paho.CallbackAPIVersion.VERSION1, client_id="Player", userdata=None, protocol=paho.MQTTv5)
    
    # enable TLS for secure connection
    client.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
    # set username and password
    client.username_pw_set(username, password)
    # connect to HiveMQ Cloud on port 8883 (default for MQTT)
    time.sleep(2) # wait for GameClient to start first
    client.connect(broker_address, broker_port)

    # setting callbacks, use separate functions like above for better visibility
    client.on_subscribe = on_subscribe # Can comment out to not print when subscribing to new topics
    client.on_message = on_message
    client.on_publish = on_publish # Can comment out to not print when publishing to topics

    lobby_name = "FirstLobby"
    player = "Player1"

    client.subscribe(f"games/{lobby_name}/lobby")
    client.subscribe(f'games/{lobby_name}/+/game_state')
    client.subscribe(f'games/{lobby_name}/scores')

    client.publish("new_game", json.dumps({'lobby_name':lobby_name,
                                            'team_name':'Team1',
                                            'player_name' : player}))
    time.sleep(1)
    

    # create thread to run 2 loops at the same time
    subscriber_loop_thread = threading.Thread(target=client.loop_forever)
    subscriber_loop_thread.start()

    time.sleep(1)
    print("Player1...")
    # client.publish(f"games/{lobby_name}/start", "START")



    # client.publish(f"games/{lobby_name}/start", "STOP")


    # client.loop_forever()
