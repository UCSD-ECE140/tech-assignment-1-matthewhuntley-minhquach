#!/bin/bash

# Start GameClient.py in one terminal
gnome-terminal -- python3 GameClient.py

# Start AutoPlayer1.py in another terminal with "START" as input
gnome-terminal -- python3 AutoPlayer1.py

# Start AutoPlayer2.py in another terminal with "START" as input
gnome-terminal -- python3 AutoPlayer2.py


# TODO: in terminal
# chmod +x start_game.sh (optional)
# ./start_game.sh

