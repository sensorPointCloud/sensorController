from pyb import Pin

def get_config():
    conf = {

        'motor3'   : {'pin_a_dir': Pin.cpu.B8 , 'pin_a_TIMx': 4, 'pin_a_TIMch': 3,
                      'pin_b_dir': Pin.cpu.B9 , 'pin_b_TIMx': 4, 'pin_b_TIMch': 4,
                      'deadband_upper': 53 },
        'motor2'   : {'pin_a_dir': Pin.cpu.E5 , 'pin_a_TIMx': 9, 'pin_a_TIMch': 1,
                      'pin_b_dir': Pin.cpu.E6 , 'pin_b_TIMx': 9, 'pin_b_TIMch': 2,
                      'deadband_upper': 53  },
        'motor1'   : {'pin_a_dir': Pin.cpu.D12, 'pin_a_TIMx': 4, 'pin_a_TIMch': 1,
                      'pin_b_dir': Pin.cpu.D13, 'pin_b_TIMx': 4, 'pin_b_TIMch': 2,
                      'deadband_upper': 53  },
        'encoder3' : {'pin_a' : Pin.cpu.E9 , 'pin_a_TIMx': 1, 'pin_a_TIMch': 1,
                      'pin_b' : Pin.cpu.E11, 'pin_b_TIMx': 1, 'pin_b_TIMch': 2,
                      'period': (4*11*1012-1)},
        'encoder2' : {'pin_a' : Pin.cpu.A15, 'pin_a_TIMx': 2, 'pin_a_TIMch': 1,
                      'pin_b' : Pin.cpu.B3 , 'pin_b_TIMx': 2, 'pin_b_TIMch': 2,
                      'period': (4*11*1012-1)},
        'encoder1' : {'pin_a' : Pin.cpu.B4 , 'pin_a_TIMx': 3, 'pin_a_TIMch': 1,
                      'pin_b' : Pin.cpu.B5 , 'pin_b_TIMx': 3, 'pin_b_TIMch': 2,
                      'period': (4*11*1012-1)},

        'motor_with_encoder_1' : {'motor': 'motor1', 'encoder': 'encoder1', 'loop_timer': 12},
        'motor_with_encoder_2' : {'motor': 'motor2', 'encoder': 'encoder2', 'loop_timer': 13},
        'motor_with_encoder_3' : {'motor': 'motor3', 'encoder': 'encoder3', 'loop_timer': 14},



        'led'                  : {'pin': Pin.cpu.F7, 'pin_TIMx': 11, 'pin_TIMch': 1, 'frequency': 100000},
        'lan'                  : {'address' : ('169.254.39.102', '255.255.0.0', '169.254.39.1', '169.254.39.1')},
        'socket'               : {'ip' : '169.254.39.115', 'port' : 1234},
        'cam_out'              : {'pin' : Pin.cpu.F2},
        'cam_in'               : {'pin' : Pin.cpu.E3},
    }

    #need to be created outside dict in order to reference it
    conf['motor3_limit_switch_top_upper']    = {'pin': Pin.cpu.C7, 'active_low': True }
    conf['motor3_limit_switch_top_lower']    = {'pin': Pin.cpu.A6, 'active_low': True }
    conf['motor2_limit_switch_bottom_upper'] = {'pin': Pin.cpu.D15, 'active_low': True }
    conf['motor2_limit_switch_bottom_lower'] = {'pin': Pin.cpu.F12, 'active_low': True }

    return conf