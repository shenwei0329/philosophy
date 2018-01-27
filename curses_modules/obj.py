# -*- coding: UTF-8 -*-
#
#   对象类 Obj
#   ==========
#   社区群体实体
#
#

from policy import Policy
import resource, basic
import uuid


class Obj:
    """
    群体：
    """

    def __init__(self, name, init_x, init_y, ch, color):
        self.name = name
        _fn = "dot%s.txt" % self.name
        self.backup = basic.BackUp(_fn)
        self.chr = ch
        self.color = color
        self.V = (0., 0., 0., 0.,)
        self.P = []
        self.policy = Policy()
        self.X = init_x + self.policy._func()
        self.Y = init_y + self.policy._func()
        self.load()

    def move(self):
        self.V = self.policy.getPolicy()
        self.X = self.X + (self.V[0]-self.V[2])
        self.Y = self.Y + (self.V[1]-self.V[3])

    def getPosition(self):
        return int(self.X), int(self.Y), self.chr, self.color

    def save(self):
        _data = {
            "x": self.X,
            "y": self.Y,
            "ch": self.chr,
            "c": self.color,
            "persons": []
        }
        for _p in self.P:
            _data['persons'].append(_p.show_name())
            _p.save()
        self.backup.save(_data)

    def load(self):
        _info = self.backup.load()
        if _info is not None:
            self.X = _info["x"]
            self.Y = _info["y"]
            self.chr = _info["ch"]
            self.color = _info["c"]
            for _name in _info["persons"]:
                self.P.append(resource.Ps(_name))
        else:
            """初值：每个群体100人
            """
            for _i in range(100):
                """个体姓名
                """
                _name = "%s-%s" % (self.name, uuid.uuid4())
                self.P.append(resource.Ps(_name))

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
