# Rewarming and Vitrifying Organoids

This is my senior design project at UNCC for the year 2023-2024. This repository contains all the code and the wiring diagram for the machine that we built. Send an email [here](mailto:awarudka@uncc.edu) for questions or if you are the future team working on this device. 

## architecture
There are two main components to this project. A react website (todo) that can be used to control the device, view active temperatures, etc (written in typescript, in the src/ directory). The main part of the project lies under the backend/ directory, which contains standard Python code to interface with the electronics. 

### react website
To start the react website in dev mode, install pnpm, then run
```bash
pnpm install
```
to add all dependencies. Then you can start the website with 
```bash
pnpm run dev
```

The goal is to have website served at the HTTP port (port 80) on the raspberry pi (it should then be accessible at http://organoids.local on the eduroam network).


### python backend
The backend portion is divided into communications (logging, database, drivers, and eventual websocket/api integration for the website). 

There is a simple SQLite database that keeps track of user preferences, temperature readings during the preheating process, and other misc information. The logging module is not fully fleshed out yet, but I imagine that eventually it can be used to warn the user when thermocouple readings are inaccurate, when things get disconnected, etc. 

Most of the code is under the drivers/ directory. Each file is a mini-library containing a class that makes it easier to use that particular component. ```display.py``` is a library I wrote from scratch to implement an interactive menu on a LCD character display. It includes support for toggle-able items, live updating content, actions on press, and a bit more. 

There is also a fully (okay, not fully) working version of the Snake game (under ```games/```) that's playable using the arrow keys on the keypad. 

You can start the device by running ```./run.sh``` from the root directory. You might have to create a virtual environment and install all the dependencies using pip before, though.


## things to improve:

1. This codebase is quite large, coming in at around 1200 lines of code (you can measure using ```./lc.sh```). I'm certain some of these components could be re-written to be more efficient. 
2. The electronics and wiring could be laid out way better. Right now, there are wires all over the place and I'm sure that with a little more thought it could look a lot prettier. 
3. There is no physical kill switch (in the rare event that something happens). This might have to be placed between the power supply and the wall outlet.
4. There are also a lot of other issues with the actual design of the device, and I really think the best way forward is to make a brand new device that's more compact and uses a more powerful heating element to speed up the preheating process (which takes around 5 minutes now).
5. The thermocouple wires are a little bit fragile (the only way to fix this was to solder them, but because we were prototyping we left it out.)
6. Half of this project is camelCase, and the other half is snake_case. Snake case is superior; I hope this gets fixed soon. 
7. In order to prevent multiple sources writing to the display at the same time, I had to implement updating flags. It's not 100% foolproof, but it's a lot better than without the flags. Sometimes, if you're too fast or unlucky, the display will bug out. 