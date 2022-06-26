import math
import time


class LinearTrajectory(object):
    """
    Trajectory representation for a linear motion

    v|  pa,ta_________pb,tb
     |      //        \\
     |_____//__________\\_______> t
       pi,ti             pf,tf
           <--duration-->
    """

    def __init__(self, pi, pf, velocity, acceleration, ti=None):
        if ti is None:
            ti = time.time()
        self.ti = ti
        self.pi = pi = float(pi)
        self.pf = pf = float(pf)
        self.velocity = velocity = float(velocity)
        self.acceleration = acceleration = float(acceleration)
        self.p = pf - pi
        self.dp = abs(self.p)
        self.positive = pf > pi

        try:
            full_accel_time = velocity / acceleration
        except ZeroDivisionError:
            # piezo motors have 0 acceleration
            full_accel_time = 0
        full_accel_dp = 0.5 * acceleration * full_accel_time ** 2

        full_dp_non_const_vel = 2 * full_accel_dp
        self.reaches_top_vel = self.dp > full_dp_non_const_vel
        if self.reaches_top_vel:
            self.top_vel_dp = self.dp - full_dp_non_const_vel
            self.top_vel_time = self.top_vel_dp / velocity
            self.accel_dp = full_accel_dp
            self.accel_time = full_accel_time
            self.duration = self.top_vel_time + 2 * self.accel_time
            self.ta = self.ti + self.accel_time
            self.tb = self.ta + self.top_vel_time
            if self.positive:
                self.pa = pi + self.accel_dp
                self.pb = self.pa + self.top_vel_dp
            else:
                self.pa = pi - self.accel_dp
                self.pb = self.pa - self.top_vel_dp
        else:
            self.top_vel_dp = 0
            self.top_vel_time = 0
            self.accel_dp = self.dp / 2
            try:
                self.accel_time = math.sqrt(2 * self.accel_dp / acceleration)
            except ZeroDivisionError:
                self.accel_time = 0
            self.duration = 2 * self.accel_time
            self.velocity = acceleration * self.accel_time
            self.ta = self.tb = self.ti + self.accel_time
            if self.positive:
                pa_pb = pi + self.accel_dp
            else:
                pa_pb = pi - self.accel_dp
            self.pa = self.pb = pa_pb
        self.tf = self.ti + self.duration

    def position(self, instant=None):
        """Position at a given instant in time"""
        if instant is None:
            instant = time.time()
        if instant < self.ti:
            raise ValueError("instant cannot be less than start time")
        if instant > self.tf:
            return self.pf
        dt = instant - self.ti
        p = self.pi
        f = 1 if self.positive else -1
        if instant < self.ta:
            accel_dp = 0.5 * self.acceleration * dt ** 2
            return p + f * accel_dp

        p += f * self.accel_dp

        # went through the initial acceleration
        if instant < self.tb:
            t_at_max = dt - self.accel_time
            dp_at_max = self.velocity * t_at_max
            return p + f * dp_at_max
        else:
            dp_at_max = self.top_vel_dp
            decel_time = instant - self.tb
            decel_dp = 0.5 * self.acceleration * decel_time ** 2
            return p + f * dp_at_max + f * decel_dp

    def instant(self, position):
        """Instant when the trajectory passes at the given position"""
        d = position - self.pi
        dp = abs(d)
        if dp > self.dp:
            raise ValueError("position outside trajectory")

        dt = self.ti
        if dp > self.accel_dp:
            dt += self.accel_time
        else:
            return math.sqrt(2 * dp / self.acceleration) + dt

        top_vel_dp = dp - self.accel_dp
        if top_vel_dp > self.top_vel_dp:
            # starts deceleration
            dt += self.top_vel_time
            decel_dp = abs(position - self.pb)
            dt += math.sqrt(2 * decel_dp / self.acceleration)
        else:
            dt += top_vel_dp / self.velocity
        return dt

    def __repr__(self):
        return "{0}({1.pi}, {1.pf}, {1.velocity}, {1.acceleration}, {1.ti})" \
            .format(type(self).__name__, self)


class Motion(object):
    """Describe a single motion"""

    def __init__(self, pi, pf, velocity, acceleration, hard_limits, ti=None):

        # TODO: take hard limits into account (complicated).
        # For now just shorten the movement
        self.hard_limits = low_limit, high_limit = hard_limits
        if pf > high_limit:
            pf = high_limit
        if pf < low_limit:
            pf = low_limit
        self.trajectory = LinearTrajectory(pi, pf, velocity, acceleration, ti)


CONFIG = dict(
    hard_low_limit=float('-inf'),
    hard_high_limit=float('+inf'),
    sign=1,
    step_size=1000,
    acceleration=0.125, # acceleration time (s)
    slew_rate=10000,    # speed in (steps/s)
    backlash=0,         # backlash
    low_limit=-180,     # low_limit dial units
    high_limit=180,     # high_limit dial units
    offset=0,           # (user units) in future move to settings
)


class Motor(object):

    def __init__(self, name, config, dial_position=0):
        self.name = name
        self.config = dict(CONFIG, **config)
        self._dial_position = dial_position
        self._motion = None

    def __getattr__(self, name):
        return self.config[name]

    def __repr__(self):
        return '{0}({1})'.format(type(self).__name__, self.name)

    @property
    def position(self):
        return self._dial_position + self.offset


    @property
    def velocity(self):
        return self.slew_rate / self.step_size

    @property
    def accel(self):
        if self.acceleration:
            return self.velocity / self.acceleration
        else:
            return float('inf')

    def _get_motion(self):
        t = time.time()
        if self._motion:
            self._dial_position = self._motion.trajectory.position(t)
            if self._motion.trajectory.tf <= t:
                self._motion = None
        return self._motion

    @property
    def moving(self):
        return self._get_motion() is not None

    @property
    def move_done(self):
        return 1 if self.moving else 0

    def start_motion(self, to):
        if self.moving:
            raise RuntimeError('motor is busy')
        self._motion = Motion(self.position, to,
                              self.velocity,
                              self.accel,
                              (self.hard_low_limit, self.hard_high_limit))

    @property
    def dial_position(self):
        motion = self._get_motion()
        return self._dial_position

    @property
    def offset(self):
        return self.config['offset']

    @offset.setter
    def offset(self, offset):
        self.config['offset'] = offset

    def abort(self):
        self._get_motion()
        self._motion = None
