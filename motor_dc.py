from pyb import Timer, Pin
import time
from state import state_organizer
import stm
import pyb


class limit_switch():
    def __init__(self, pin_number, pin_on_low_func, pin_on_high_func, pull='UP'):
        if pull == 'UP':
            self.switch_pin = Pin(pin_number, Pin.IN, Pin.PULL_UP)
        elif pull == 'DOWN':
            self.switch_pin = Pin(pin_number, Pin.IN, Pin.PULL_DOWN)
        elif pull == 'NONE':
            self.switch_pin = Pin(pin_number, Pin.IN)
        else:
            raise ValueError("Not valid pull pin. Valid options are UP, DOWN and NONE")

        self.pin_on_low_func = pin_on_low_func
        self.pin_on_high_func = pin_on_high_func

        # Force pin to execute on init. This will detect if switch was engaged before program start
        self.change_pin_state(self.switch_pin)

        self.switch_pin.irq(self.change_pin_state, trigger=(Pin.IRQ_FALLING | Pin.IRQ_RISING))

    def change_pin_state(self, pin):
        if pin() == 0:
            self.pin_on_low_func()
        elif pin() == 1:
            self.pin_on_high_func()


class motor():  # Motor with 1 pwm and 2 en
    def __init__(self, ena_pin_number, enb_pin_number, pwm_pin_number, pwm_timer_number, pwm_channel_number):
        # Enable pins
        self.ena_pin = Pin(ena_pin_number, Pin.OUT)
        self.enb_pin = Pin(enb_pin_number, Pin.OUT)
        # Setting up pwm:
        self.timer_pwm = Timer(pwm_timer_number, freq=100000)
        self.pwm_pin = Pin(pwm_pin_number, Pin.OUT)
        self.pwm = self.timer_pwm.channel(pwm_channel_number, Timer.PWM, pin=self.pwm_pin)
        self.position = 0
        self.velocity = 0
        self.power = 0

    # Power values <-100,100>
    def set_power(self, power):
        self.power = power
        if power < 0:
            self.ena_pin.value(0)
            self.enb_pin.value(1)
            power = power * -1
        else:
            self.ena_pin.value(1)
            self.enb_pin.value(0)

        if power < 5 and power > 0.01:
            power = 5
        if power > 100:
            power = 100
        self.pwm.pulse_width_percent(power)

    def get_power(self):
        return self.power

    def ramp_to_simple(self, power, time_ms=1000):
        current_power = self.get_power()
        delta_power = power - current_power
        if time_ms <= 0:
            time_ms = 1
        step = delta_power / time_ms
        set_power = current_power
        for i in range(0, time_ms):
            set_power = set_power + step
            self.set_power(set_power)
            time.sleep_us(1000)
            # pyb.udelay(1000)


class motor_2pwm():  # Motor with 2 pwm and 0 en
    def __init__(self, pwm1_pin_number, pwm1_timer_number, pwm1_channel_number, pwm2_pin_number, pwm2_timer_number,
                 pwm2_channel_number, deadband_upper):
        self.pwm1_timer_number = pwm1_timer_number
        self.pwm1_pin_number = pwm1_pin_number
        self.pwm1_channel_number = pwm1_channel_number

        self.pwm2_timer_number = pwm2_timer_number
        self.pwm2_pin_number = pwm2_pin_number
        self.pwm2_channel_number = pwm2_channel_number

        self.activate_pin_dir_1()
        self.activate_pin_dir_2()

        self.power = 0
        self.deadband_upper = deadband_upper

    def deactivate_pin_dir_1(self):
        Pin(self.pwm1_pin_number, Pin.IN)

    def deactivate_pin_dir_2(self):
        Pin(self.pwm2_pin_number, Pin.IN)

    def activate_pin_dir_1(self):
        self.timer_pwm1 = Timer(self.pwm1_timer_number, freq=100000)
        self.pwm_pin1 = Pin(self.pwm1_pin_number, Pin.OUT)
        self.pwm1 = self.timer_pwm1.channel(self.pwm1_channel_number, Timer.PWM, pin=self.pwm_pin1)

    def activate_pin_dir_2(self):
        self.timer_pwm2 = Timer(self.pwm2_timer_number, freq=100000)
        self.pwm_pin2 = Pin(self.pwm2_pin_number, Pin.OUT)
        self.pwm2 = self.timer_pwm2.channel(self.pwm2_channel_number, Timer.PWM, pin=self.pwm_pin2)

    # Power values <-100,100>
    def set_power(self, power):
        self.power = power

        if power < 0:
            en1 = 0
            en2 = 1
            power = power * -1
        else:
            en1 = 1
            en2 = 0

        if power < 0.01:
            power = 0
        elif power > 100:
            power = 100
        else:
            power = power + self.deadband_upper  # offset power st motor moves at power == 1

        self.pwm1.pulse_width_percent(power * en1)
        self.pwm2.pulse_width_percent(power * en2)

    def get_power(self):
        return self.power

    def ramp_to_simple(self, power, time_ms=1000):
        current_power = self.get_power()
        delta_power = power - current_power
        if time_ms <= 0:
            time_ms = 1
        step = delta_power / time_ms
        set_power = current_power
        for i in range(0, time_ms):
            set_power = set_power + step
            self.set_power(set_power)
            time.sleep_us(1000)
            # pyb.udelay(1000)


class encoder():

    # Period value is inclusive. counter will have max value == period
    # Only use channel 1 a and 2 of timer, and never 1N and 2N
    def __init__(self, pin_number_a, pin_number_b, period, timer_number):
        # Timer registers, needed for direction
        regs = [0, stm.TIM1, stm.TIM2, stm.TIM3, stm.TIM4, stm.TIM5, stm.TIM6, stm.TIM7, stm.TIM8, stm.TIM9, stm.TIM10,
                stm.TIM11, stm.TIM12]
        self.direction_register = regs[timer_number] + stm.TIM_CR1
        # Pins
        pin_a = Pin(pin_number_a, Pin.IN)  # PE9
        pin_b = Pin(pin_number_b, Pin.IN)  # PE11
        # Encoder
        self.encoder = Timer(timer_number, prescaler=0, period=period)
        self.encoder.channel(1, Timer.ENC_AB, pin=pin_a)
        self.encoder.channel(2, Timer.ENC_AB, pin=pin_b)
        self.period = period
        self.rollover = 0
        self.encoder.callback(self.loop_counter_rollover)

    def loop_counter_rollover(self, timer):
        if self.get_direction() == 0:
            self.rollover = self.rollover + 1
        else:
            self.rollover = self.rollover - 1

    def get_degrees(self):
        return 360.0 * self.encoder.counter() / self.period  # encoder period is inclusive

    def get_degrees_total(self):
        return self.rollover * 360.0 + self.get_degrees()

    def get_direction(self):
        return (stm.mem32[self.direction_register] & 0x10) >> 4


class motor_with_encoder():
    def __init__(self, motor, encoder, loop_timer_number):  # loop_timer_number TIMn
        self.motor = motor
        self.encoder = encoder
        self.state_org = state_organizer()
        self.init_loop_timer(loop_timer_number)

    # Set an unused timer number, the values are based on a timer freq of 108MHz
    def init_loop_timer(self, timer_number):
        self.rollover = 0
        self.loop_timer_period = 0xffff
        self.loop_timer = Timer(timer_number, prescaler=10800,
                                period=self.loop_timer_period)  # timer fq = 10000Hz 1s = 10000
        self.loop_timer.callback(self.loop_counter_rollover)

    def loop_counter_rollover(self, timer):
        self.rollover = self.rollover + 1

    # loop timer in milli seconds
    def get_loop_timer_ms(self):
        ctr = self.loop_timer.counter() + self.rollover * self.loop_timer_period
        return ctr / 10

    # loop timer in seconds
    def get_loop_timer_s(self):
        ctr = self.loop_timer.counter() + self.rollover * self.loop_timer_period
        return ctr / 10000

    def reset_loop_timer(self):
        self.rollover = 0
        self.loop_timer.counter(0)

    def get_deg_error(self, deg_set, deg):
        err = deg_set - deg
        if err < -180:  # 0 - 300 = -300 -> 60
            err = err + 360
        elif err > 180:  # 270 - 30 = 240 -> -120
            err = err - 360
        return err

    def set_position(self, deg_set, k_p, k_i, acceptable_error=0.05):
        # timer = Timer(12, prescaler=10800, period=0xffff) #timer fq = 10000Hz 1s = 10000
        _I = 0  # I@t-1
        a = 0
        err_prev = 999
        _t = self.get_loop_timer_s()
        while True:
            a = a + 1
            if a > 1000:
                print('Error: ', err, 'Power: ', power, 'K: ', K, 'I: ', I, 'Degrees: ', self.encoder.get_degrees())
                a = 0

            # asyncio.sleep(0.001) #Loop time is 1ms
            time.sleep_us(1000)
            t = self.get_loop_timer_s()
            dt = t - _t

            self.reset_loop_timer()
            deg = self.encoder.get_degrees()
            err = self.get_deg_error(deg_set, deg)
            if abs(err) < acceptable_error:
                err = 0
                if err == err_prev:
                    print('Final Error: ', err, 'Power: ', power, 'K: ', K, 'I: ', I, 'Degrees: ',
                          self.encoder.get_degrees())
                    return
                err_prev = err
            I = dt * err + _I  # Integrator

            # Cap integrator
            if I > 5:
                I = 5
            elif I < -5:
                I = -5
            _I = I
            K = err  # Proportional
            power = k_p * K + k_i * I
            self.motor.set_power(power)

            _t = t

    # returns the average velocity since the last call
    def get_angular_velocity(self):
        # try this: https://docs.micropython.org/en/v1.9.3/pyboard/reference/speed_python.html#caching-object-references
        vel = self.state_org.vel  # requires fewer object lookups

        time = self.get_loop_timer_s()
        position = self.encoder.get_degrees_total()

        dPosition = position - vel._pos
        dt = time - vel._time

        vel._pos = position
        vel._time = time

        return dPosition / dt

    def set_velocity(self, vel_set, k_p, k_i, loop_time_us=1000, filter_val=1):
        _v = self.get_angular_velocity()
        a = 0
        _t = self.get_loop_timer_s()
        _I = 0
        _vel = 0
        while True:
            a = a + 1
            if a > 200:
                print('v filter: ', v, 'Velocity: ', vel_act, 'Error: ', err, 'Power: ', power, 'K: ', K, 'I: ', I,
                      '\n')
                a = 0

            time.sleep_us(loop_time_us)
            t = self.get_loop_timer_s()
            dt = t - _t

            vel_act = self.get_angular_velocity()
            v = vel_act * filter_val + _v * (1 - filter_val)

            err = vel_set - v

            I = dt * err + _I  # Integral
            K = err  # Proportional
            power = k_p * K + k_i * I
            self.motor.set_power(power)

            _t = t
            _I = I
            _v = v
