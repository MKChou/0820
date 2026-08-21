import Adafruit_SSD1306
from PIL import Image, ImageDraw, ImageFont
import RPi.GPIO as GPIO
import time

FONT_SIZE = 16

GPIO_TRIGGER = 23
GPIO_ECHO = 24

def display_setup():

    disp = Adafruit_SSD1306.SSD1306_128_32(rst = 0)

    disp.begin()
    disp.clear()
    disp.display()

    return disp

def display(disp, text: str):

    width = disp.width
    height = disp.height
    image = Image.new('1', (width, height))
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("./ARIALUNI.TTF", FONT_SIZE)

    draw.rectangle((0, 0, width, height), outline=0, fill=0)
    draw.text((0, 0), "Distance: ", font=font, fill=255)
    draw.text((4, 15), text, font=font, fill = 255)
    disp.image(image)
    disp.display()

def get_distance():
    GPIO.setmode(GPIO.BCM)

    GPIO_TRIGGER = 23
    GPIO_ECHO = 24
    GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
    GPIO.setup(GPIO_ECHO, GPIO.IN)
   
    GPIO.output(GPIO_TRIGGER, True)
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)

    startTime = time.time()
    endTime = time.time()
    while GPIO.input(GPIO_ECHO) == 0:
        startTime = time.time()
    while GPIO.input(GPIO_ECHO) == 1:
        endTime = time.time()

    timeElapsed = endTime - startTime
    distance = (timeElapsed*34300) / 2
    
    #GPIO.cleanup()
    
    return distance

if __name__ == '__main__':
    disp = display_setup()
    try:
        print("Press ^C to terminate")
        while True:
            distance = round(get_distance(), 1)
            display(disp, str(distance))
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("terminated")
    finally:
        disp.clear()
        disp.display()
