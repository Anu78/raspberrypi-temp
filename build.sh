#!/bin/bash

# build frontend
pnpm build

# setup nginx and copy files
sudo cp -r build/* /var/www/html/
sudo cp nginx.conf /etc/nginx/sites-available/default
sudo systemctl restart nginx

# start backend
env/bin/python3 run.py