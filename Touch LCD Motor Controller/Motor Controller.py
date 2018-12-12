import sys
from math import sqrt
import time
import RPi.GPIO as GPIO
from evdev import InputDevice, categorize, ecodes

dev = InputDevice('/dev/input/event0')

GPIO.setmode(GPIO.BCM)

motor_pins_1 = [5, 6, 12, 13,]
motor_pins_2 = [4, 17, 27, 22]
for pin in motor_pins_1:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, False)
for pin in motor_pins_2:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, False)


seq1 = [[0, 1, 1, 1],
       [1, 0, 1, 1],
       [1, 1, 0, 1],
       [1, 1, 1, 0],
       [0, 1, 1, 1],
       [1, 0, 1, 1],
       [1, 1, 0, 1],
       [1, 1, 1, 0]]

seq2 = [[1, 1, 1, 0],
       [1, 1, 0, 1],
       [1, 0, 1, 1],
       [0, 1, 1, 1],
       [1, 1, 1, 0],
       [1, 1, 0, 1],
       [1, 0, 1, 1],
       [0, 1, 1, 1]]



state = 0
x = []
y = []

def rotation(delta,w,motor,dir):
    global motor_pins_1,motor_pins_2,seq1,seq2
    if motor == 1:
        pins = motor_pins_1
    if motor == 2:
        pins = motor_pins_2
    if dir == 'cw':
        seq = seq2
    if dir == 'acw':
        seq = seq1
    StepCount = len(seq)
    StepDir = 1
    StepCounter = 0
    for x in xrange(0, int(sqrt(int(delta)))):
        for pin in range(0, 4):
            xpin = pins[pin]
            if seq[StepCounter][pin] != 0:
                GPIO.output(xpin, True)
            else:
                GPIO.output(xpin, False)

        StepCounter += StepDir

        if (StepCounter >= StepCount):
            StepCounter = 0
        if (StepCounter < 0):
            StepCounter = StepCount + StepDir

        time.sleep(w)


def touch(event):
    global x, y, state, WaitTime
    if event.value == 1:
        state = 1
        x = []
        y = []
    else:
        if len(x) < 2 or len(y) < 2:
            return
        state = 0
        delta_y = y[-1] - y[0]
        delta_x = x[-1] - x[0]
        d = sqrt(delta_x ** 2 + delta_y ** 2)
        if d > 1800:
            TH = 400
        else:
            TH = 200
        if d < 100:
            return
        # print('start:\t{}, {}'.format(x[0], y[0]))
        # print('end:\t{}, {}\n'.format(x[-1], y[-1]))
        # print('delta x:\t{}'.format(delta_x))
        # print('delta y:\t{}'.format(delta_y))
        if abs(abs(delta_x) - abs(delta_y)) < TH:

            if delta_x > 0 and delta_y > 0:
                print('SE')
                rotation(d,.1,2,'acw')
            if delta_x > 0 and delta_y < 0:
                print('NE')
                rotation(d, .02, 2, 'cw')
            if delta_x < 0 and delta_y > 0:
                print('SW')
                rotation(d, .1, 2, 'cw')
            if delta_x < 0 and delta_y < 0:
                print('NW')
                rotation(d, .02, 2, 'acw')

        else:

            if abs(delta_x) > abs(delta_y):
                if delta_x > 0:
                    print('R')
                    rotation(d, .02, 1, 'cw')
                else:
                    print('L')
                    rotation(d, .1, 1, 'cw')
            else:
                if delta_y < 0:
                    print('U')
                    rotation(d, .02, 1, 'acw')
                else:
                    print('D')
                    rotation(d, .1, 1, 'acw')

        '''if x[-1] - x[0] > 0:
            WaitTime = 10 / float(1000)
            m1_delta_x(x[-1] - x[0])
        else:
            WaitTime = 10 / float(250)
            m1_delta_x(x[0] - x[-1])
        '''


def sync():
    global x, y, state
    if len(x) == len(y):
        return
    l = min([len(x), len(y)])
    x = x[:l - 1]
    y = y[:l - 1]


for event in dev.read_loop():
    if event.code == 330 and event.type == 1:
        touch(event)
    if state == 0:
        continue
    if event.code == 0 and event.type == 0:
        sync()
    if event.code == 0 and event.type == 3:
        x.append(event.value)
    if event.code == 1 and event.type == 3:
        y.append(event.value)

