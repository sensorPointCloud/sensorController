import motor_dc
import time
import pyb
from pyb import Pin, Timer
import setup
import stm


#TEST DC MOTOR
#m_dc = test1.get_dc_motor()
dual_pwm = True
m_dc = setup.get_motor3()
encoder = setup.get_encoder3()
#Setting up motor with encoder:
#motor_with_encoder = motor_dc.motor_with_encoder(motor=m_dc,encoder=encoder,loop_timer_number=12)
m3 = setup.get_motor_with_encoder3()
m2 = setup.get_motor_with_encoder2()
m1 = setup.get_motor_with_encoder1()
lsw21,lsw22 = setup.get_limit_switches_motor2()
lsw3 = setup.get_limit_switches_motor3()

motor_with_encoder = m3

##EXTERNAL TEST
def run_motor(power):
    global motor_with_encoder
    motor_with_encoder.motor.ramp_to_simple(power,1500)
    while True:
        print('degrees: %s, degrees total: %s' % (motor_with_encoder.encoder.get_degrees(), motor_with_encoder.encoder.get_degrees_total()) )

##

##AUTOMTIC TEST

#Testing on/off motor

def motor_power(power):
    m_dc.set_power(power)
    pw     = m_dc.get_power()
    pw_act = m_dc.pwm.pulse_width_percent()
    if power<0:
        pw_act = pw_act*-1
    print('get power: %s, act power: %s, set power: %s' % (pw, pw_act, power) )
    
    within_offset_pw_act   = value_within_offset(pw_act, power, 0.1)
    assert pw == power
    assert within_offset_pw_act

def motor_power_dual_pwm(power):
    m_dc.set_power(power)
    deadband_upper = m_dc.deadband_upper
    pw     = m_dc.get_power()
    
    if power >= 0:
        pw_act = m_dc.pwm1.pulse_width_percent()
    else:
        pw_act = m_dc.pwm2.pulse_width_percent()

    if power<0:
        pw_act = pw_act*-1
    print('get power: %s, act power: %s, set power: %s' % (pw, pw_act, power) )
    
    within_offset_pw_act   = value_within_offset(pw_act, power, 0.1+deadband_upper)
    assert pw == power
    assert within_offset_pw_act

def motor_power_test():
    global dual_pwm

    if dual_pwm:
        #dual pwm
        power = 12
        motor_power_dual_pwm(power)
        power = -13
        motor_power_dual_pwm(power)
        power = 0
        motor_power_dual_pwm(power)

    else:
        #single pwm
        power = 12
        motor_power(power)
        power = -13
        motor_power(power)
        power = 0
        motor_power(power)





def ramp_test(power, ramp_time):
    t1 = pyb.micros()
    #ramp_time = 1000
    #power = 75
    m_dc.ramp_to_simple(power, ramp_time)
    t2 = pyb.micros()
    delta_time = (t2-t1)/1000
    pw = m_dc.get_power()
    print('ramp')
    print('dt: %s, dt_expected: %s' % (delta_time, ramp_time) )
    print('power: %s, power_expected: %s' % (pw, power) )
    within_percent_dt   = value_within_percentage(delta_time, ramp_time, 5)
    within_offset_pw   = value_within_offset(pw, power, 0.01)
    assert within_percent_dt
    assert within_offset_pw

def ramp_to_simple_test():
    ramp_test(75, 1000)
    ramp_test(27.9, 2532)
    ramp_test(100, 500)
    ramp_test(-100, 2000)
    ramp_test(-79, 574)
    ramp_test(-89, 774)
    ramp_test(0, 1500)
    
    #ramp_test(10, 0): expect 1ms , manual test:

    t1 = pyb.micros()
    ramp_time = 0
    ramp_time_expected = 1
    power = 6
    m_dc.ramp_to_simple(power, ramp_time)
    t2 = pyb.micros()
    delta_time = (t2-t1)/1000
    pw = m_dc.get_power()
    print('ramp')
    print('dt: %s, dt_expected: %s' % (delta_time, ramp_time_expected) )
    print('power: %s, power_expected: %s' % (pw, power) )
    within_offset_dt  = value_within_offset(delta_time, ramp_time_expected, 0.3)
    within_offset_pw  = value_within_offset(pw, power, 0.01)
    assert within_offset_dt
    assert within_offset_pw

    m_dc.ramp_to_simple(0,100)


#TEST ENCODER
#enc_period  = (4*11*1012-1) #period is inclusive!! period=1 will give values 0 and 1
#encoder = motor_dc.encoder(pin_number_a='D6', pin_number_b='D5', period=enc_period, timer_number=1)


# Test encoder, motor not moving
def degrees_equal_test():
    time.sleep(2)
    value1 = encoder.get_degrees()
    time.sleep(0.5)
    value2 = encoder.get_degrees()
    print('value1: %s, value2: %s' % (value1, value2) )
    assert value1 == value2
    print("degrees_test passed!")

# Test encoder, motor moving
def get_direction_test():
    m_dc.ramp_to_simple(20,500)
    dir1 = encoder.get_direction()
    m_dc.ramp_to_simple(-20,500)
    dir2 = encoder.get_direction()
    m_dc.ramp_to_simple(0,500)
    print('dir1: %s, dir2: %s' % (dir1,dir2) )
    assert dir1 != dir2
    print("get_direction_test passed!")


def get_degrees_total_test():
    # reset encoder value:
    encoder.encoder.counter(0)

    deg1 = encoder.get_degrees_total()
    # rotate more than 1 round pos dir
    m_dc.ramp_to_simple(100, 1000)
    time.sleep_ms(6000)
    deg2 = encoder.get_degrees_total()

    print('deg start: %s, deg end: %s' % (deg1, deg2) )
    print('delta deg should be more than 360')
    assert (deg2-deg1) > 360

    # reset encoder value:
    encoder.encoder.counter(0)
    
    deg1 = encoder.get_degrees_total()
    # rotate more than 1 round pos dir
    m_dc.ramp_to_simple(-100, 1000)
    time.sleep_ms(6000)
    deg2 = encoder.get_degrees_total()

    print('deg start: %s, deg end: %s' % (deg1, deg2) )
    print('delta deg should be less than -360')
    assert (deg2-deg1) < -360
    m_dc.ramp_to_simple(0, 1000)


# Test encoder, delta degrees
def get_deg_error_test():
    value1 = motor_with_encoder.encoder.get_degrees()
    motor_with_encoder.motor.set_power(30)
    time.sleep(0.5)
    motor_with_encoder.motor.set_power(0)
    value2 = motor_with_encoder.encoder.get_degrees()
    print('value1 [deg]: %s, value2 [deg]: %s' % (value1, value2) ) 
    assert value1 != value2
    print('get_deg_error_test passed!')


def value_within_percentage(value_check, value_set, percentage):
    frac = percentage/100
    if value_set >=0:
        return value_check <= value_set*(1+frac) and value_check >= value_set*(1-frac)
    else:
        return value_check >= value_set*(1+frac) and value_check <= value_set*(1-frac)


def value_within_offset(value_check, value_set, offset):
    return value_check <= value_set+offset and value_check >= value_set-offset


# Test loop timer
def loop_timer_test():
    motor_with_encoder.reset_loop_timer() #reset timer
    value2_us = 10000
    time.sleep_us(value2_us)       # sleep for 100 microseconds

    value1_ms = motor_with_encoder.get_loop_timer_ms()


    motor_with_encoder.reset_loop_timer()
    time.sleep_us(value2_us)       # sleep for 100 microseconds

    value1_s = motor_with_encoder.get_loop_timer_s()


    value2_ms = value2_us/1000
    value2_s = value2_us/1000000
    print('time.sleep_us(x) is not accurate. Acceptable with 1%% error')
    print('value [ms]: %s, value2 [ms]: %s' % (value1_ms, value2_ms) )    
    print('value [s]: %s, value2 [s]: %s' % (value1_s, value2_s) ) 
    # within_1_percent_ms = value1_ms <= value2_ms*1.01 and value1_ms >= value2_ms*0.99
    # within_1_percent_s = value1_s <= value2_s*1.01 and value1_s >= value2_s*0.99
    
    acceptable_percentage = 1
    within_1_percent_ms   = value_within_percentage(value1_ms, value2_ms, acceptable_percentage)
    within_1_percent_s    = value_within_percentage(value1_s, value2_s, acceptable_percentage)
    assert within_1_percent_ms
    assert within_1_percent_s
    print("loop_timer_test passed!")


def loop_timer_long_test():
    motor_with_encoder.reset_loop_timer() #reset timer
    value2_ms = 10000
    time.sleep_ms(value2_ms)       # sleep for 10 seconds

    value1_ms = motor_with_encoder.get_loop_timer_ms()

    print('counter value: ', motor_with_encoder.loop_timer.counter())
    print('time.sleep_us(x) is not accurate. Acceptable with 1%% error')
    print('value [ms]: %s, value2 [ms]: %s' % (value1_ms, value2_ms) )    
    
    acceptable_percentage = 1
    within_1_percent_ms   = value_within_percentage(value1_ms, value2_ms, acceptable_percentage)
    assert within_1_percent_ms

    print("loop_timer_long_test passed!")


def set_position_test(set_point):
    set_point_degrees = set_point
    acceptable_offset = 0.05
    motor_with_encoder.set_position(set_point_degrees, k_p=1, k_i=0, acceptable_error=acceptable_offset)
    final_position = motor_with_encoder.encoder.get_degrees()
    value_within_acceptable_error = value_within_offset(final_position, set_point_degrees,acceptable_offset)
    print('Position [deg]: %s, Set point [deg]: %s, Acceptable offset: %s' % (final_position, set_point_degrees, acceptable_offset) ) 
    print('Offset error: %s' % (set_point_degrees-final_position))
    assert value_within_acceptable_error
    print('set_position_test passed!')


def get_angular_velocity_test():
    m_dc.ramp_to_simple(30, 1000)
    motor_with_encoder.get_angular_velocity() #first call to init vars
    time.sleep_ms(3000) #stabilaze velocity
    motor_with_encoder.get_angular_velocity()
    time.sleep_us(5*1000)
    v1 = motor_with_encoder.get_angular_velocity()
    time.sleep_us(500*1000)
    v2 = motor_with_encoder.get_angular_velocity()
    time.sleep_us(2*1000)
    v3 = motor_with_encoder.get_angular_velocity()
    time.sleep_us(1*1000)
    v4 = motor_with_encoder.get_angular_velocity()
    time.sleep_us(500)
    v5 = motor_with_encoder.get_angular_velocity()
    m_dc.ramp_to_simple(0, 1000)

    acceptable_error = 1
    print('Acceptable error [%%]: %s', acceptable_error)
    print('Vel 1 [deg/s]: %s, Vel 2 [deg/s]: %s' % (v1, v2) ) 
    print('Vel 3 [deg/s]: %s, Vel 4 [deg/s]: %s' % (v3, v4) ) 
    print('Vel 5 [deg/s]: %s' % (v5) )
    value_within_acceptable_percentage1 = value_within_percentage(v1, v2, acceptable_error)
    value_within_acceptable_percentage2 = value_within_percentage(v1, v3, acceptable_error)
    value_within_acceptable_percentage3 = value_within_percentage(v1, v4, acceptable_error)
    value_within_acceptable_percentage4 = value_within_percentage(v1, v5, acceptable_error)

    assert value_within_acceptable_percentage1
    assert value_within_acceptable_percentage2
    assert value_within_acceptable_percentage3
    assert value_within_acceptable_percentage4
    print('get_angular_velocity_test passed!')


# test direction stm hardware
def quick_test(power, delay_ms):
    m_dc.set_power(power)
    
    while True:
        time.sleep_ms(delay_ms)
        v = motor_with_encoder.get_angular_velocity()
        direction = (stm.mem32[stm.TIM1 + stm.TIM_CR1] & 0x10) >> 4
        reg = bin(stm.mem32[stm.TIM1 + stm.TIM_CR1])
        print('[deg/s]: %s, direction: %s, reg: %s' % (v, direction, reg))


def run_all_tests():
    print('\nmotor_power_test')
    motor_power_test()
    print('\nramp_to_simple_test')
    ramp_to_simple_test()
    print('\ndegrees_equal_test')
    degrees_equal_test()
    print('\nget_direction_test')
    get_direction_test()
    print('\nget_degrees_total_test')
    get_degrees_total_test()
    print('\nget_deg_error_test')
    get_deg_error_test()
    print('\nloop_timer_test')
    loop_timer_test()
    print('\nloop_timer_test 10s')
    loop_timer_long_test()
    print('\nset_position_test 1')
    set_position_test(179)
    print('\nset_position_test 2')
    set_position_test(1)
    print('\nset_position_test 3')
    set_position_test(-20)
    print('\nset_position_test 4')
    set_position_test(-380)
    print('\nset_position_test 5')
    set_position_test(470)

    print('\nget_angular_velocity_test')
    get_angular_velocity_test()
    
    print('\nALL TEST PASSED\n\n')


