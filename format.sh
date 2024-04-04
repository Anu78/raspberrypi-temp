#!/bin/bash

pnpm exec prettier . --write

black backend/drivers/*.py
black backend/communications/*.py
black backend/run.py

