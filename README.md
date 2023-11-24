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
| [Adafruit Itsy Bitsy m4 express]([https://www.adafruit.com/product/5000](https://www.adafruit.com/product/3800))                                    | Uses CircuitPython 8.0.0 |
| [Piston](https://www.amazon.com/dp/B08CZ3WP1Q?smid=A37DFQ476WZ5XM&ref_=chk_typ_imgToDp&th=1) | TAILONZ|
| [5 Port pneumatic solenoid valve]([https://www.adafruit.com/product/4409](https://www.amazon.com/dp/B081PTW87K?psc=1&ref=ppx_yo2ov_dt_b_product_details)) |TAILONZ| 
| [EPLZON MOSFET Switch Drive Module DC 5V-36V 15A](https://www.amazon.com/dp/B09LLR675M?psc=1&ref=ppx_yo2ov_dt_b_product_details)                             |
| [Air supply hose](https://www.amazon.com/dp/B07R4ZT2BC?psc=1&ref=ppx_yo2ov_dt_b_product_details)                      | Amazon  |
| [Micro Self-priming Diapharm Pump](https://www.amazon.com/gp/product/B09ZX4TFNG/ref=ppx_yo_dt_b_asin_title_o07_s00?ie=UTF8&psc=1)      | Amazon  |


## Current state of project
The project is mostly complete. There aren't any current bugs to fix or capabilities that need to be added.

The unit has been running for two+ months without issue with roughly 100+ pumping events.

The original 6v pump was significantly underpowered (needs to pump water up 6') and was replaced with a 12v pump that works flawlessly.
