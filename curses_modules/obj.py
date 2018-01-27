# -*- coding: UTF-8 -*-
#
#   对象类 Obj
#   ==========
#

from policy import Policy
import json
import resource


class Obj:

    def __init__(self, name, init_x, init_y, ch, color):
        self.name = name
        self.chr = ch
        self.color = color
        self.V = (0., 0., 0., 0.,)
        self.P = []
        """初值：每个群体100人
        """
        for _i in range(100):
            self.P.append(resource.Ps())
        self.policy = Policy()
        try:
            self.load()
        except:
            self.X = init_x + self.policy._func()
            self.Y = init_y + self.policy._func()

    def move(self):
        self.V = self.policy.getPolicy()
        self.X = self.X + (self.V[0]-self.V[2])
        self.Y = self.Y + (self.V[1]-self.V[3])

    def getPosition(self):
        return int(self.X), int(self.Y), self.chr, self.color

    def save(self):
        fp = open('dot%s.txt' % self.name, 'w')
        json.dump({"x":self.X, "y":self.Y, "ch":self.chr, "c":self.color}, fp)
        fp.close()

    def load(self):
        fp = open('dot%s.txt' % self.name, 'r')
        _info = json.load(fp)
        self.X = _info["x"]
        self.Y = _info["y"]
        self.chr = _info["ch"]
        self.color = _info["c"]
        fp.close()

    def time_scale(self, ts):
        _alive = 0
        _requirment = 0
        for _p in self.P:
            if ts % 24 == 0:
                _requirment += _p.life_one_day()
            else:
                _requirment += _p.show()
            if _p.alive():
                    _alive += 1
        return _alive, _requirment
