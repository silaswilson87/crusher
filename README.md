# Autonomous Pump1

## Overview
Example of an autonomous sensor component.

The primary purpose of this project is to help define and debug a Spring Boot Application that monitors remote sensor components.

It uses three water level measurement sensors for added datapoints to help validate that the hardware is functioning as intended.

**Note**: To see debug output, create empty file with name "debug" in the root of the feather.

## Component diagram
[Diagram created with PlantUML (pump_component.puml) ](https://plantuml.com/)
![Pump state diagram](documentation/pump_component.png?raw=true)


## State diagram 
(as programmed in pumpingcontroller.py, method check_state)

[Diagram created with PlantUML (pump-state-diagram.puml) ](https://plantuml.com/)

![Pump state diagram](documentation/pump-state-diagram.png?raw=true)

## Liquid Level Sensor
(Liquid Level Sensor Switch (Single Float) SPST-NO Output Panel Mount, M8 Thread)


![Pump wiring diagram](documentation/59630-1-T-02-A.jpg?raw=true)

## Pump
![Pump](documentation/51wQLqJQSUL._AC_SX569_.jpg?raw=true)

## Hardware diagram
(The FeatherWing is stacked on ESP32-S2 so there isn't any wiring between them)
![Pump wiring diagram](documentation/pump_Sketch_bb.jpg?raw=true)

## HW List

| Component                                                                                                                              | Notes                    |
|----------------------------------------------------------------------------------------------------------------------------------------|--------------------------|
| [Adafruit ESP32-S2](https://www.adafruit.com/product/5000)                                                                             | Uses CircuitPython 8.0.0 |
| [Liquid Level Sensor](https://www.digikey.com/en/products/detail/littelfuse-inc./59630-1-T-02-A/4771999?utm_adgroup=General&utm_term=) | Littelfuse Inc.|
| [Adafruit STEMMA Non-Latching Mini Relay - JST PH 2mm](https://www.adafruit.com/product/4409)                                          |
| [Adafruit FeatherWing OLED](https://www.adafruit.com/product/4650)                                                                     |
| [5v Buck Converter](https://www.amazon.com/gp/product/B0B779ZYN1/ref=ppx_yo_dt_b_asin_title_o08_s00?ie=UTF8&th=1)                      | Amazon  |
| [Micro Self-priming Diapharm Pump](https://www.amazon.com/gp/product/B09ZX4TFNG/ref=ppx_yo_dt_b_asin_title_o07_s00?ie=UTF8&psc=1)      | Amazon  |


## Current state of project
The project is mostly complete. There aren't any current bugs to fix or capabilities that need to be added.

The unit has been running for two+ months without issue with roughly 100+ pumping events.

The original 6v pump was significantly underpowered (needs to pump water up 6') and was replaced with a 12v pump that works flawlessly.