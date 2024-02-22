# Rewarming and Vitrifying Organoids 

This is the respository for my 2023-2024 senior design project. This code is intended to run on a raspberry pi. See the roadmap for future plans, parts required, and other general information. 

## What's in this repository
This repository, by the end of May 2024, will contain the following: 
1. 3d models and schematics of our device 
2. Electrical wiring diagrams 
3. All the source code (drivers for all the components and the web server)
4. Detailed documentation of the source code and architecture of the application. 

The goal is to ensure that anyone that works on this device in the future will be able to pick up where I left off and continue improving and iterating over the design. 

## Required parts 
This project involves the following parts: 
1. Two silicone rubber flex heaters
2. A stepper motor & a limit switch
3. A joystick (and thus an analog to digital converter)
4. 3 thermocouple readers (MAX6675 in this case, but there might be a switch to a more accurate module later)

see __parts.md__ for detailed information on all the parts.

## Roadmap

A general overview/timeline of what is complete and what needs to be done. 
### Drivers
- [ ] lcd display driver (functioning menu, action, update system)
- [ ] speaker (jukebox and alert noises)
- [ ] joystick + adc converter  
- [ ] heater controller (adjustable buck converter)
- [ ] maintain accurate temperature on heaters (integral) 
- [ ] thermocouple readers (serial interface)
- [ ] stepper motor / limit switch
### Webserver / other
- [ ] SQLite database setup / python driver
- [ ] Websockets for internal communications and event streaming
- [ ] react+vite website  

** more will be added in the future when all the drivers are written. **
## General Information