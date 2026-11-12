#!/bin/bash
# Скрипт для упрощения жизни линуксоидам на bspwm

./main.py &
sleep 0.7
bspc node -t floating
wait
