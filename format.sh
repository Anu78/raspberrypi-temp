#!/bin/bash

echo "formatting ts"
pnpm exec prettier . --write >

echo "formatting py"
black backend/drivers/*.py
black backend/communications/*.py
black backend/run.py

