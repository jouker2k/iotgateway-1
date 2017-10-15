#ref http://www.vikki.in/raspberry-pi-blinking-led-in-morse/
import RPi.GPIO as GPIO
import time

CODE = {' ': ' ',
        "'": '.----.',
        '(': '-.--.-',
        ')': '-.--.-',
        ',': '--..--',
        '-': '-....-',
        '.': '.-.-.-',
        '/': '-..-.',
        '0': '-----',
        '1': '.----',
        '2': '..---',
        '3': '...--',
        '4': '....-',
        '5': '.....',
        '6': '-....',
        '7': '--...',
        '8': '---..',
        '9': '----.',
        ':': '---...',
        ';': '-.-.-.',
        '?': '..--..',
        'A': '.-',
        'B': '-...',
        'C': '-.-.',
        'D': '-..',
        'E': '.',
        'F': '..-.',
        'G': '--.',
        'H': '....',
        'I': '..',
        'J': '.---',
        'K': '-.-',
        'L': '.-..',
        'M': '--',
        'N': '-.',
        'O': '---',
        'P': '.--.',
        'Q': '--.-',
        'R': '.-.',
        'S': '...',
        'T': '-',
        'U': '..-',
        'V': '...-',
        'W': '.--',
        'X': '-..-',
        'Y': '-.--',
        'Z': '--..',
        '_': '..--.-'}

COLOUR = {'RED': 17, 'YELLOW': 22}

GPIO.setmode (GPIO.BCM)
GPIO.setwarnings(False)

class DotDash(object):
    def __init__(self, colour):
        self.COLOUR_CODE = COLOUR[colour.upper()]
        GPIO.setup(self.COLOUR_CODE,GPIO.OUT)

    def dot(self):
            GPIO.output(self.COLOUR_CODE, True)
            time.sleep(0.2)
            GPIO.output(self.COLOUR_CODE, False)
            time.sleep(0.2)

    def dash(self):
            GPIO.output(self.COLOUR_CODE, True)
            time.sleep(0.5)
            GPIO.output(self.COLOUR_CODE, False)
            time.sleep(0.2)


def morse_code(input_, colour):
    morse = DotDash(colour)

    for letter in input_:
        for symbol in CODE[letter.upper()]:
            if symbol == '-':
                morse.dash()
            elif symbol == '.':
                morse.dot()
            else:
                time.sleep(0.5)
        time.sleep(0.5)
    return True
    GPIO.cleanup()


#morse_code("test", "yellow")
