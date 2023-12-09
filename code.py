import board
import digitalio
import time
from digitalio import DigitalInOut, Direction, Pull

mosfet = digitalio.DigitalInOut(board.D13)  # mosfset switch controlling a 12V Pnuematic solenoid valve between digital pin12 and ground
mosfet.direction = digitalio.Direction.OUTPUT  # Output directed control signal

# status lights #
red = digitalio.DigitalInOut(board.D12)  # Automatic state
red.direction = digitalio.Direction.OUTPUT
green = digitalio.DigitalInOut(board.D11)  # Mosfet trigger light
green.direction = digitalio.Direction.OUTPUT
blue = digitalio.DigitalInOut(board.D10)  # Manual state
blue.direction = digitalio.Direction.OUTPUT

touch_pin = DigitalInOut(board.D7)  # Push button
touch_pin.direction = digitalio.Direction.INPUT
touch_pin.pull = Pull.DOWN
touch_val = touch_pin.value  # Assign Boolean value of pin D7 to variable

manual_pin = DigitalInOut(board.D2)  # Manual mode
manual_pin.direction = digitalio.Direction.INPUT
manual_pin.pull = Pull.DOWN
manual_pin_val = manual_pin.value  # Assign Boolean value of pin D2 to variable

auto_pin = DigitalInOut(board.D1)  # Automatic mode
auto_pin.direction = digitalio.Direction.INPUT
auto_pin.pull = Pull.DOWN
auto_pin_val = auto_pin.value  # Assign Boolean value of pin D1 to variable

def manual():  # Logic for manual mode of button
        print("-Manual- Initiate valve")
        green.value = True
        mosfet.value = True
        time.sleep(.2)
        green.value = False
        mosfet.value = False
        
def auto():  # Logic for button
        print("-Auto- Initiate valve")
        green.value = True
        mosfet.value = True
        time.sleep(.6)
        green.value = False
        mosfet.value = False
        time.sleep(.6)

def manual_button():  # Manual Button logic initializer
    if str(touch_val) == "True":
        manual()

def auto_button():  # Automatic Button logic initializer
    if str(touch_val) == "True":
        auto()

print("(-Base-level 0)")
print("Current slide switch Manual orientation = " + str(manual_pin_val))
print("Current slide switch Automatic orientation = " + str(auto_pin_val))
print("Current push button value = " + str(touch_val))

while True:
    touch_val = touch_pin.value
    manual_pin_val = manual_pin.value
    auto_pin_val = auto_pin.value
    if manual_pin.value :  # Calls manual fuction of push button mosfet control
        blue.value = True
        red.value = False
        if manual_pin.value and touch_pin.value:
            manual()            
    elif auto_pin.value :  # Calls auto fuction of push button mosfet control
        red.value = True
        blue.value = False
        if auto_pin.value and touch_pin.value:
            auto()
