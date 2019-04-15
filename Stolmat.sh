#!/bin/bash
PROMPT_COMMAND='echo -ne "\033]0;Stolmat.sh\007"'
export PYTHONPATH="${PYTHONPATH}:/home/pi/Desktop/BigBoy/"
python3 ./Plank/Server.py