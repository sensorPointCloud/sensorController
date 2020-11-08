class state_params():
    def __init__(self):
        self._pos  = 0
        self._vel  = 0
        self._acc  = 0
        self._time = 0

class state_organizer():
    def __init__(self):
        self.pos = state_params()
        self.vel = state_params()
        self.acc = state_params()