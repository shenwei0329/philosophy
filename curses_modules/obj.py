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
        _fn = "dot%s" % self.name
        self.backup = basic.BackUp(_fn)
        self.chr = ch
        self.color = color
        self.V = (0., 0., 0., 0.,)

        """群体的个人集合
        """
        self.P = []

        """性别情况
        """
        self.male = 0
        self.female = 0

        """怀孕人数
        """
        self.mating = 0

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
                _p = resource.Ps(_name)
                if _p.show_sex() == 'Male':
                    self.male += 1
                else:
                    self.female += 1
                self.P.append(_p)
        else:
            """初值：每个群体100人
            """
            for _i in range(100):
                """个体姓名
                """
                _name = "%s-%s" % (self.name, uuid.uuid4())
                _p = resource.Ps(_name)
                if _p.show_sex() == 'Male':
                    self.male += 1
                else:
                    self.female += 1
                self.P.append(_p)

    def time_scale(self, ts):
        """
        时标处理器
        :param ts: 时标
        :return: 存活个数，需求总量，男性个数，女性个数，怀孕人数
        """
        _alive = 0
        _requirment = 0
        _male = []
        _female = []
        self.mating = 0
        for _p in self.P:
            if ts % 24 == 0:
                _requirment += _p.life_one_day()
                """收集满足交配条件的个人
                """
                if _p.can_mating("Male"):
                    _male.append(_p)
                if _p.can_mating("Female"):
                    _female.append(_p)
            else:
                _requirment += _p.show()
            if _p.alive():
                    _alive += 1
            else:
                """从人群中删除"""
                self.P.remove(_p)

        if len(_male) > 0 and len(_female) > 0:
            """若有满足交配条件的两性，则允许交配
            """
            for _m in _male:
                _m.mating('Male')
            for _f in _female:
                if _f.mating('Female'):
                    self.mating += 0
        for _p in self.P:
            if _p.is_mating():
                self.mating += 1
            if _p.birth():
                """新生一代
                """
                _name = "%s-%s" % (self.name, uuid.uuid4())
                _p = resource.Ps(_name)
                if _p.show_sex() == 'Male':
                    self.male += 1
                else:
                    self.female += 1
                self.P.append(_p)

        return _alive, _requirment, self.male, self.female, self.mating
