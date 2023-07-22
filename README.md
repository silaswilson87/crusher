# Autonomous Pump1

## Overview
Example of an autonomous sensor component.

The primary purpose of this project is to help define and debug a Spring Boot Application that monitors remote sensor components.

It uses three water level measurement sensors for added datapoints to help validate that the hardware is functioning as intended.

**Note**: To see debug output, create empty file with name "debug" in the root of the feather.

## Component diagram
![Pump state diagram](documentation/pump_component.png?raw=true)


## State diagram 
(as programmed in pumpingcontroller.py, method check_state)
![Pump state diagram](documentation/pump-state-diagram.png?raw=true)

## Liquid Level Sensor
(Liquid Level Sensor Switch (Single Float) SPST-NO Output Panel Mount, M8 Thread)

![Pump wiring diagram](documentation/59630-1-T-02-A.jpg?raw=true)

## Hardware diagram
v![Pump wiring diagram](documentation/pump_Sketch_bb.jpg?raw=true)

## HW List

| Component                                                              | Notes                           |
|------------------------------------------------------------------------|---------------------------------|
| [Adafruit ESP32-S2](https://www.adafruit.com/product/5000)             |Uses CircuitPython 8.0.0-beta.5 |
| [Adafruit ESP32-S3](https://www.adafruit.com/product/5477)             |Will use next time              |
| [Simple Water Detection Sensor](https://www.adafruit.com/product/4965) |                                 |
| [Adafruit STEMMA Non-Latching Mini Relay - JST PH 2mm](https://www.adafruit.com/product/4409)|


## Current state of project
The water level measurement and pump on/off logic is functional, but needs more testing.

I'm using a breadboad in my test bed and the wiring is not reliable. I'll be moving to a soldered prototype board to test the reliability.

The state machine in pumping_controller.py is more convoluted that I'd like. I'll revisit and clean up later.

The REST interface has been coded, but not tested. I'm working on the backend and will come back to this project when the backend is ready.
