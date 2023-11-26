import board
import digitalio
import time
import touchio

valve = digitalio.DigitalInOut(board.D12)
valve.direction = digitalio.Direction.OUTPUT
touch_pin = touchio.TouchIn(board.D7)
last_touch_val = False  # holds last measurement
toggle_value = False  # holds state of toggle switch


def led():
    if toggle_value:
        print("Debug Moffset off")
        valve.value = False
    else:
        while toggle_value != True:
            print("Debug function "+strval+" valve cycle")
            valve.value = True
            time.sleep(0.5)
            valve.value = False
            time.sleep(0.5)
        
        
while True:
  touch_val = touch_pin.value
  if touch_val != last_touch_val:
    if touch_val:
      toggle_value = not toggle_value   # flip toggle
      print("Debug toggle state", toggle_value)
      led()
      else:
          continue
  last_touch_val = touch_val
  strval = str(toggle_value)
