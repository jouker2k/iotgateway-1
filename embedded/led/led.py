import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
COLOUR = {'RED': 17, 'YELLOW': 22}

def on(colour):
    try:
        colour = colour.upper()
        GPIO.setup(COLOUR[colour], GPIO.OUT)
        GPIO.output(COLOUR[colour], GPIO.HIGH)
        return True
    except Exception as e:
        return e

def off(colour):
    try:
        colour = colour.upper()
        GPIO.setup(COLOUR[colour], GPIO.OUT)
        GPIO.output(COLOUR[colour], GPIO.LOW)
        return True
    except Exception as e:
        return e

def blink(colour, number_of_times):
    for x in range(0, number_of_times):
        on(colour)
        time.sleep(0.2)
        off(colour)
        time.sleep(0.2)
    return True


#off("yellow")
