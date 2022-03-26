#!/bin/bash
tmux new -s gacha-bot -c -d
tmux send-keys -t gacha-bot 'python3.9 -m pipenv run python bot.py' C-m
