#import motor_dc_test

#motor_dc_test.run_all_tests()

import setup
import pyb
import time


#joystick
joystic_y = pyb.ADC('A0')
joystic_x = pyb.ADC('A1')

def joystic_val():
    global joystic_x, joystic_y
    y = joystic_y.read()-2047
    if abs(y) < 100:
        y = 0

    y = y/20.48

    x = joystic_x.read()-2047
    if abs(x) < 100:
        x = 0

    x = x/20.48
    return x,y

m1    = setup.get_motor_with_encoder1()

m2    = setup.get_motor_with_encoder2()
m2_ls = setup.get_limit_switches_motor2()

m3    = setup.get_motor_with_encoder3()
m3_ls = setup.get_limit_switches_motor3()

m3=m1
while True:
    x,y = joystic_val()
    x = x/10
    y = y/10

    m2.motor.set_power(x)
    m3.motor.set_power(y)
    print(x, y, m2.encoder.get_degrees(), m3.encoder.get_degrees())
    time.sleep_ms(100)