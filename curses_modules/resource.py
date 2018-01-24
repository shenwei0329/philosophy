# -*- coding: UTF-8 -*-
#
#   资源类 Resource
#   ===============
#

import math

class E:

    def __init__(self):
        pass

    def _dlt_E(self, time_scale):
        _x = time_scale % 360
        math.sin((2 * math.pi / 360) * _x)

class Resource:

    def __init__(self, MAX_X, MAX_Y):
        pass

    def get(self, x, y):
        pass

    def refresh(self, time_scale):
        pass
