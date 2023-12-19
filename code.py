import board
import digitalio
import time
from digitalio import DigitalInOut, Direction,

red = digitalio.DigitalInOut(board.D12)  # Automatic state
red.direction = digitalio.Direction.OUTPUT
green = digitalio.DigitalInOut(board.D11)  # Mosfet trigger light - Mosfset switch controlling a 12V Pnuematic solenoid valve
green.direction = digitalio.Direction.OUTPUT
blue = digitalio.DigitalInOut(board.D10)  # Manual state
blue.direction = digitalio.Direction.OUTPUT

irbeam = digitalio.DigitalInOut(board.D13)  # Mosfset switch controlling a 12V Pnuematic solenoid valve between digital pin12 and ground
irbeam.direction = digitalio.Direction.INPUT
irbeam.pull = digitalio.Pull.UP
irbeam_val = irbeam.value  # Assign Boolean value of pin D7 to variable as a string

touch_pin = DigitalInOut(board.D7)  # Push button
touch_pin.direction = digitalio.Direction.INPUT
touch_val = touch_pin.value  # Assign Boolean value of pin D7 to variable as a string

manual_pin = DigitalInOut(board.D2)  # Manual mode
manual_pin.direction = digitalio.Direction.INPUT
manual_pin_val = manual_pin.value  # Assign Boolean value of pin D2 to variable as a string

auto_pin = DigitalInOut(board.D1)  # Automatic mode
auto_pin.direction = digitalio.Direction.INPUT
auto_pin_val = auto_pin.value  # Assign Boolean value of pin D1 to variable as a string


def manual():  # Controller for manual mode of button
    print("-Manual- Initiate valve")
    green.value = True
    time.sleep(0.1)
    green.value = False


def auto():  # Control for manual mode of button
    while True:
        if auto_pin.value and irbeam.value == False:
            print("-Auto- Initiate valve")
            green.value = True
            time.sleep(1.1)
            green.value = False
            time.sleep(1.1)
        else:
            break


print("(level 0 - Natural Bias)")
print("Current IR beam orientation = " + str(irbeam_val))
print("Current slide switch Manual orientation = " + str(manual_pin_val))
print("Current slide switch Automatic orientation = " + str(auto_pin_val))
print("Current push button value = " + str(touch_val))

while True:
    if manual_pin.value:  # Calls manual function of push button mosfet control
        blue.value = True
        red.value = False
        if manual_pin.value and touch_pin.value:
            manual()
    elif auto_pin.value:  # Calls auto function of push button mosfet control
        red.value = True
        blue.value = False
        if auto_pin.value and touch_pin.value == True:
            auto()

