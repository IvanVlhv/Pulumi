#!/bin/bash
set -e
exec > /var/log/user-data.log 2>&1
yum update -y
yum install -y git python3
cd /home
if [ ! -d SnakeGame ]; then
  git clone https://github.com/IvanVlhv/SnakeGame.git
fi
cd SnakeGame
pip3 install -r requirements.txt
nohup python3 app.py &

