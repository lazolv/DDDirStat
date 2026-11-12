#!/bin/bash
# Скрипт для упрощения жизни линуксоидам на bspwm

bspc rule -a "*" -o state=floating && ./main.py
