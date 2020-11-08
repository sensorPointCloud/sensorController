import setup
import pyb
from pyb import Pin
import time
import config
import motor_dc

# Motors
m1    = setup.get_motor_with_encoder1()
m2    = setup.get_motor_with_encoder2()
m3    = setup.get_motor_with_encoder3()
m2_limit_sw_up, m2_limit_sw_down = setup.get_limit_switches_motor2()
m3_limit_sw_up, m3_limit_sw_down = setup.get_limit_switches_motor3()

# Laser
led = setup.get_led()
led.pulse_width_percent(0)

# Camera
pin_cam_capture = None
frame_number = 0

# Network
nic = setup.get_lan()
s = setup.get_socket()


values = 4
frames = 300
acquisition_rate_hz = 500
n_frames = 2
idx_max = values*frames*n_frames - 1
angles_time = [i for i in range(0, values*frames*n_frames)]

idx = 0
transfer_values = False

current_from_number = 0


def on_frame_capture_start(pin):
    global m2, m3, idx, angles_time, transfer_values, current_from_number
    if idx > idx_max:
        print('idx error')
        return
    
    e1 = m1.encoder.get_degrees_total()
    e2 = m2.encoder.get_degrees_total()
    e3 = m3.encoder.get_degrees_total()
    angles_time[idx]   = time.ticks_ms()
    angles_time[idx+1] = int(e1*1000)
    angles_time[idx+2] = int(e2*1000)
    angles_time[idx+3] = int(e3*1000)
    
    current_from_number += 1
    idx += 4


pin_capture, pin_switch = setup.get_camera_pins(on_frame_capture_start)


def send_all_angles_and_time(error=False):
    global angles_time, s
    t1 = time.ticks_us()
    if error:
        s.sendall(bytes(str(angles_time) +',' + current_from_number + ',frame_error\n', 'utf8'))
    else:
        s.sendall( bytes(str(angles_time)+'\n', 'utf8') )
    line = s.readline()
    t2 = time.ticks_us()
    print(line, 'time to send and rec: ', (t2-t1)/1000)


def capture(n=1, print_angles=False):
    global idx, angles_time, pin_capture
    for i in range(0, n):
        pin_capture(1)
        time.sleep_us(250)
        pin_capture(0)
        time.sleep_us(250)
        print("idx: %s " % idx)
    
    if print_angles:
        print("angles_time: ", angles_time)


# need to run pyb.delay in order to trigger interrupt
def test_cam_capture_single():
    global idx, pin_capture
    idx_start = idx
    ms = 1
    pin_capture(1)
    pyb.delay(ms)
    pin_capture(0)
    pyb.delay(1000)
    assert idx == (idx_start + frames*values)


def cam_capture_multi():
    global idx, pin_capture
    for _ in range(0, n_frames):
        idx_start = idx
        pin_capture(1)
        pyb.delay(1)
        pin_capture(0)
        capture_time = int((frames / acquisition_rate_hz) * 1000) + 2
        pyb.delay(capture_time)
        try:
            assert idx == (idx_start + frames*values)
        except:
            # Frame error
            idx = 0
            return True
    idx = 0
    return False # No error


def power(angle_min=-10, angle_max=0, start=False):
    global m3
    angle = m3.encoder.get_degrees_total()
    m_power = m3.motor.get_power()
    power_value_neg = -1.5
    power_value_pos = 1

    if start is True:
        m3.motor.set_power(-power_value_neg)
        return None

    if angle < angle_min:
        if m_power < 0:
            m3.motor.set_power(0)
        else:
            m3.motor.set_power(power_value_pos)
    elif angle > angle_max:
        if m_power > 0:
            m3.motor.set_power(0)
        else:
            m3.motor.set_power(power_value_neg)


def snap_and_send():
    frame_error = cam_capture_multi()
    send_all_angles_and_time(frame_error)
    return frame_error


def test_long_run():
    frames = 0
    for _ in range(0, 1000):
        frame_error = cam_capture_multi()
        send_all_angles_and_time(frame_error)
        frames += n_frames
        print('Run amount of frames: ', frames)


def move_z(run_ms=100):
    global m1
    print(m1.encoder.get_degrees_total())
    m1.motor.set_power(2.5)
    time.sleep_ms(run_ms)
    m1.motor.set_power(0)
    print(m1.encoder.get_degrees_total())


def power_and_send():
    global m1, m3, led, idx
    led.pulse_width_percent(100)
    power(start=True)
    
    # make som initial frames along e.g. straight wall:
    for _ in range(8):
        snap_and_send()
        power(angle_min=-10, angle_max=10)

    try:
        while True:
            for _ in range(10):
                snap_and_send()
                power(angle_min=-10, angle_max=10)
            move_z(200)
            #wait for z stabilize
            time.sleep_ms(500)

            if ( m1.encoder.get_degrees_total() > 270.0 ):
                break

    except KeyboardInterrupt as ki:
        print('Interrupted')
        m1.motor.set_power(0)
        m3.motor.set_power(0)
        led.pulse_width_percent(0)
        idx = 0
        raise ki

    print('Finished')
    m1.motor.set_power(0)
    m3.motor.set_power(0)
    led.pulse_width_percent(0)
    idx = 0

    
def zero_motor(motor, limit_switch, degrees_offset, direction_to_limit_switch, up_power=1):
    m = motor
    # move to limit switch top, then:
    if direction_to_limit_switch == -1:
        m.motor.set_power(-up_power)
    elif direction_to_limit_switch == 1:
        m.motor.set_power(up_power)
    while limit_switch.switch_pin() == 1:
        pass
    m.encoder.encoder.counter(0)
    m.motor.set_power(0.1)
    pyb.delay(500)
    m.motor.set_power(0)
    
    # move to 69.135 degrees
    degrees = degrees_offset
    m.set_position(degrees,0.1, 0, 0.02)
    pyb.delay(1000)
    m.set_position(degrees, up_power*4, 0, 0.02)
    pyb.delay(1000)
    m.set_position(degrees, up_power*12, 0, 0.02)
    # then
    m.encoder.encoder.counter(0)
    m.encoder.get_degrees()


def zero_motor3():
    global m3, m3_limit_sw_up
    degrees_offset = 69.135
    direction_to_limit_switch = -1
    zero_motor(m3, m3_limit_sw_up, degrees_offset, direction_to_limit_switch)


def zero_motor2():
    global m2, m2_limit_sw_up
    degrees_offset = 335.348
    direction_to_limit_switch = 1
    up_power = 2
    zero_motor(m2, m2_limit_sw_up, degrees_offset, direction_to_limit_switch, up_power)


# run
    # zero motors
    # power_and_send


