import config
import motor_dc
from pyb import Pin, Timer
import network
import socket


# Setup motor1 with encoder:
def get_motor1():
    return get_motor_2pwm_from_config('motor1')


def get_encoder1():
    conf = config.get_config()
    return get_encoder_from_conf('encoder1')


def get_motor_with_encoder1():
    return get_motor_with_encoder_from_conf('motor_with_encoder_1')


# Setup motor2 with encoder and limit switches:
def get_motor2():
    return get_motor_2pwm_from_config('motor2')


def get_encoder2():
    return get_encoder_from_conf('encoder2')


def get_motor_with_encoder2():
    return get_motor_with_encoder_from_conf('motor_with_encoder_2')


def get_limit_switches_motor2():
    m2 = get_motor2()
    l_up   = get_limit_switch_from_conf('motor2_limit_switch_bottom_upper', m2.deactivate_pin_dir_1, m2.activate_pin_dir_1)
    l_down = get_limit_switch_from_conf('motor2_limit_switch_bottom_lower', m2.deactivate_pin_dir_2, m2.activate_pin_dir_2)
    return l_up, l_down


# Setup motor3 with encoder and limit switches:
def get_motor3():
    return get_motor_2pwm_from_config('motor3')


def get_encoder3():
    return get_encoder_from_conf('encoder3')


def get_motor_with_encoder3():
    return get_motor_with_encoder_from_conf('motor_with_encoder_3')


def get_limit_switches_motor3():
    m3 = get_motor3()
    l_up   = get_limit_switch_from_conf('motor3_limit_switch_top_upper', m3.deactivate_pin_dir_2, m3.activate_pin_dir_2)
    l_down = get_limit_switch_from_conf('motor3_limit_switch_top_lower', m3.deactivate_pin_dir_1, m3.activate_pin_dir_1)
    return l_up, l_down


# LED
def get_led():
    return get_pwm_from_conf('led')


# LAN
def get_lan():
    return get_lan_from_conf('lan')


# SOCKET
def get_socket():
    return get_socket_from_conf('socket')


def get_camera_pins(callback):
    conf                  = config.get_config()['cam_out']
    pin_cam_start_capture = Pin(conf['pin'], Pin.OUT)
    
    conf              = config.get_config()['cam_in']
    pin_cam_interrput = conf['pin']

    pin_cam_interrput.irq(callback, trigger=Pin.IRQ_RISING)
    return pin_cam_start_capture, pin_cam_interrput


motors = {}
def get_motor_2pwm_from_config(motor):
    global motors

    try:  # if motor object already created, return it
        return motors[motor]
    except:
        print('Setting up: ', motor)

    conf = config.get_config()[motor]

    pwm1_pin_number     = conf['pin_a_dir']
    pwm1_timer_number   = conf['pin_a_TIMx']
    pwm1_channel_number = conf['pin_a_TIMch']
    pwm2_pin_number     = conf['pin_b_dir']
    pwm2_timer_number   = conf['pin_b_TIMx']
    pwm2_channel_number = conf['pin_b_TIMch']
    deadband_upper      = conf['deadband_upper']

    motors[motor] = motor_dc.motor_2pwm(pwm1_pin_number, pwm1_timer_number, pwm1_channel_number, pwm2_pin_number, pwm2_timer_number, pwm2_channel_number,deadband_upper)
    return motors[motor]


encoders = {}
def get_encoder_from_conf(encoder):
    global encoders

    try:  # if encoder object already created, return it
        return encoders[encoder]
    except:
        print('Setting up: ', encoder)
    
    conf = config.get_config()[encoder]

    pin_a     = conf['pin_a']
    pin_b     = conf['pin_b']
    period    = conf['period']
    timer_nr  = conf['pin_a_TIMx']

    encoders[encoder] = motor_dc.encoder(pin_a, pin_b, period, timer_nr)
    return encoders[encoder]


motors_with_encoder = {}
def get_motor_with_encoder_from_conf(motor_with_encoder):
    global motors_with_encoder
    try:  # if motors_with_encoder object already created, return it
        return motors_with_encoder[motor_with_encoder]
    except:
        print('Setting up: ', motor_with_encoder)

    conf    = config.get_config()[motor_with_encoder]
    motor   = get_motor_2pwm_from_config( conf['motor'] )
    encoder = get_encoder_from_conf( conf['encoder'] )
    TIMn    = conf['loop_timer']

    motors_with_encoder[motor_with_encoder] = motor_dc.motor_with_encoder(motor, encoder, TIMn)

    return motors_with_encoder[motor_with_encoder]


pwms = {}
def get_pwm_from_conf(pwm):
    global pwms
    try:  # if pwm object already created, return it
        return pwms[pwm]
    except:
        print('Setting up: ', pwm)

    conf      = config.get_config()[pwm]
    pin_nr    = conf['pin']
    frequency = conf['frequency']
    timer_nr  = conf['pin_TIMx']
    timer_ch  = conf['pin_TIMch']
    timer_pwm = Timer(timer_nr, freq=frequency)
    pwm_pin   = Pin(pin_nr, Pin.OUT)
    pwms[pwm] = timer_pwm.channel(timer_ch, Timer.PWM, pin=pwm_pin)
    
    return pwms[pwm]


limit_switches = {}
def get_limit_switch_from_conf(limit_switch,on_low_func, on_high_func):
    global limit_switches
    try:  # if limit_switch object already created, return it
        return limit_switches[limit_switch]
    except:
        print('Setting up: ', limit_switch)

    conf          = config.get_config()[limit_switch]
    pin           = conf['pin']
    limit_switches[limit_switch] = motor_dc.limit_switch(pin, on_low_func, on_high_func)

    return limit_switches[limit_switch]


lans = {}
def get_lan_from_conf(lan):
    global lans
    try:
        return lans[lan]
    except:
        print('Setting up: ', lan)
    conf    = config.get_config()[lan]
    address = conf['address']
    try:
        nic       = network.LAN()
        nic.active(True)
        nic.ifconfig(address)
        lans[lan] = nic
        return lans[lan]
    except:
        return None


sockets = {}
def get_socket_from_conf(socket_key):
    global sockets
    try:
        return sockets[socket_key]
    except:
        print('Setting up: ', socket_key)
    try:
        conf = config.get_config()[socket_key]
        ip   = conf['ip']
        port = conf['port']
        addr = socket.getaddrinfo(ip, port)[0][-1]
        s    = socket.socket()
        s.connect(addr)
        sockets[socket_key] = s
        return sockets[socket_key]
    except Exception as e:
        print('Socket with error: ', e)
        return None

