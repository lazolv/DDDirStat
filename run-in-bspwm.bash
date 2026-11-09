#!/bin/bash
# Скрипт для упрощения жизни линуксоидам на bspwm

./main.py &
sleep 0.5
bspc node -t floating
wait
