# -*- coding: UTF-8 -*-
#
#   资源类 Resource
#   ===============
#   社会资源定义
#   1）能量E
#       每一个自然资源都按时期（春夏秋冬）创造不同水平的能力当量
#   2）人口P、个人Ps
#       个人特性：
#           年龄、性别、不同性别的人对能量的需求。不同年龄段所消耗的能量当量不同（呈现sin特性）
#       人口：是个人的集合，其特征是所有个人的综合表现
#   3）按照“群”占地面积的比例分配能量
#


import math, random, uuid, time
import basic

random.seed(time.time())


class E:
    """
    能量E
    """

    def __init__(self, name):
        self.name = name
        self.backup = basic.BackUp(self.name)
        self.max_quota = 10000
        self.quota = 10
        _data = self.backup.load()
        if _data is not None:
            self.quota = _data['quota']

    def dlt_E(self, time_scale):
        _x = (float(time_scale)/24.) % 360
        self.quota -= math.cos((2 * math.pi / 360) * _x)
        if self.quota<0:
            self.quota = 0
        elif self.quota>self.max_quota:
            self.quota = self.max_quota

    def show(self):
        return self.quota

    def show_name(self):
        return self.name

    def get(self, e_quota):
        if self.quota>e_quota:
            self.quota-=e_quota
            return True
        else:
            return False

    def save(self):
        _data = {'quota': self.quota}
        self.backup.save(_data)


class Ps:
    """
    个人Ps：社会的复杂性，最终表现在个体（点）上
    1）姓名name：个体标识
    2）性别sex：Male（男性），Female（女性）
    3）消耗quota：以性别、年龄相关
    4）繁殖(reproduction)：
        - 以性别、年龄相关；女性在14～50岁间有生育能力，孕10个月，间隔1年
        - 男性生育期16～70岁
        【是否考虑“婚姻”关系，以家庭为单元，杜绝近亲婚姻，或会影响后代质量】
    5）出力(out_power)：每个男性个体，按其年龄输出其能量当量
    待加入：
    1）教育
    2）个性
    3）环境对个体的影响
    """

    def __init__(self, name):
        self.name = name
        _fn = "person-%s" % name
        self.backup = basic.BackUp(_fn)
        _person = self.backup.load()
        if _person is not None:
            self.tot_reproduction = _person['tot_reproduction']
            self.reproduction = {"pregnant":_person['pregnant'] ,"interval":_person['interval']}
            self.quota = _person['quota']
            self.age = _person['age']
            self.sex = _person['sex']
            self.dltQ = _person['dltQ']
            self.day = _person['day']
        else:
            self.tot_reproduction = 0
            """仅针对女性：怀孕pregnant：孕期；生育间隔interval
            """
            self.reproduction = {"pregnant": -1 , "interval": -1}
            self.quota = 10
            if random.random() > 0.5:
                self.sex = 'Male'
                self.dltQ = 8.
            else:
                self.sex = 'Female'
                self.dltQ = 5.
            self.day = 0
            self.age = 0
            self.save()

    def save(self):
        _person = {
            "tot_reproduction": self.tot_reproduction,
            "pregnant": self.reproduction['pregnant'],
            "interval": self.reproduction['interval'],
            "quota": self.quota,
            "age": self.age,
            "sex": self.sex,
            "dltQ": self.dltQ,
            "day": self.day,
        }
        self.backup.save(_person)

    def life_one_day(self):
        """
        个人成长
        :return:
        """
        self.day += 1
        if (self.day % 90) == 0:
            self.age += 0.25
        """人对E的需要：【0-80岁】
        """
        self.quota += self.dltQ * math.sin((math.pi/80.)*self.age)
        """孕期处理
        """
        if self.sex == 'Female':
            if self.reproduction["pregnant"] >= 0:
                """孕育过程需要能量
                """
                if self.quota > 5:
                    self.reproduction["pregnant"] += 1
                    self.quota -= 5
            elif self.reproduction["interval"] >= 0:
                self.reproduction["interval"] += 1
        return self.quota

    def show(self):
        return self.quota

    def show_name(self):
        return self.name

    def show_sex(self):
        return self.sex

    def is_mating(self):
        if self.reproduction["pregnant"]>0:
            return True
        return False

    def alive(self):
        if (self.age/360.) > 80:
            return False
        else:
            return True

    def can_mating(self, need):
        """
        判断个体是否具备交配条件
        :param need: 性别
        :return: 判断结果
        """
        if need == 'Male':
            if (self.sex == 'Male') and (self.age >= 16) and (self.age < 70) and (self.quota > 5):
                return True
        else:
            if (self.age >= 14) and (self.age < 50) and (self.quota > 3):
                if (self.reproduction["pregnant"] < 0) and \
                        ((self.reproduction["interval"] < 0) or (self.reproduction["interval"] >= 360)):
                    return True
        return False

    def mating(self, need):
        """
        交配：条件男女之间，女性满足生育条件
        :need: 交配条件，男性或女性
        :return: 是否怀孕
        """
        if not self.can_mating(need):
            return False

        if need == 'Male':
            if (self.age >= 16) and (self.age < 70) and (self.quota > 5):
                _v = random.random()
                if (_v > 0.6) and (_v < 0.8):
                    """设置受孕条件，由于繁殖太快，需要严格受孕条件
                    """
                    self.quota -= 5
                    return True
            return False
        else:
            _ret = False
            if (self.age >= 14) and (self.age < 50) and (self.quota > 3):
                if self.reproduction["pregnant"] < 0:
                    """未孕
                    """
                    _v = random.random()
                    if (_v > 0.5) and (_v < 0.8):
                        """设置受孕条件，由于繁殖太快，需要严格受孕条件
                        """
                        if (self.reproduction["interval"] < 0) or (self.reproduction["interval"] >= 360):
                            """已间隔1年
                            """
                            _ret = True
            if _ret:
                """怀孕
                """
                self.reproduction["pregnant"] = 0
                self.reproduction["interval"] = -1
                self.quota -= 3
            return _ret

    def birth(self):
        """
        生育：判断孕期情况
        :return: 是否到孕期
        """
        if self.sex == "Female":
            if self.reproduction["pregnant"] >= 300:
                """预期10个月
                """
                self.reproduction["pregnant"] = -1
                self.reproduction["interval"] = 0
                return True
        return False

    def out_power(self):
        """
        出力：每个男性个人按其年龄输出其"出力"当量
        :return: 能量当量
        """
        if self.sex == 'Male':
            if self.age > 16:
                if self.age < 20 and self.quota > 5:
                    self.quota -= 5
                    return 5
                if self.age < 30 and self.quota > 15:
                    self.quota -= 15
                    return 15
                if self.age < 40 and self.quota > 20:
                    self.quota -= 20
                    return 20
                if self.age < 50 and self.quota > 15:
                    self.quota -= 15
                    return 15
                if self.age < 60 and self.quota > 10:
                    self.quota -= 10
                    return 10
                if self.age < 70 and self.quota > 3:
                    self.quota -= 3
                    return 3
                else:
                    if self.quota > 1:
                        self.quota -= 1
                        return 1
        return 0


class Resource:

    def __init__(self, MAX_X, MAX_Y):
        self.backup = basic.BackUp('resource')
        self.MAX_X = MAX_X
        self.MAX_Y = MAX_Y
        self.E_unit = {}
        _data = self.backup.load()
        if _data is not None:
            for _x in range(self.MAX_X):
                self.E_unit[_x] = []
                for _y in range(self.MAX_Y):
                    _key = "%d-%d" % (_x, _y)
                    self.E_unit[_x].append(E(_data[_key]))
        else:
            _data = {}
            for _x in range(self.MAX_X):
                self.E_unit[_x] = []
                for _y in range(self.MAX_Y):
                    _key = "%d-%d" % (_x, _y)
                    _name = "energy-%s" % uuid.uuid4()
                    self.E_unit[_x].append(E(_name))
                    _data[_key] = _name
            self.backup.save(_data)

    def get(self, x, y, e_quota):
        if self.E_unit.has_key(x):
            return self.E_unit[x][y].get(e_quota)

    def show(self, x, y):
        if (x>0) and (x<len(self.E_unit)):
            if self.E_unit.has_key(x):
                return self.E_unit[x][y].show()

    def refresh(self, time_scale):
        _total = 0
        for _x in range(self.MAX_X):
            for _y in range(self.MAX_Y):
                self.E_unit[_x][_y].dlt_E(time_scale)
                _total += self.E_unit[_x][_y].show()
        return _total

    def save(self):
            for _x in range(self.MAX_X):
                for _y in range(self.MAX_Y):
                    self.E_unit[_x][_y].save()


def main():

    R = Resource(20, 30)
    for _i in range(0, 365*20, 10):
        R.refresh(_i)
        print R.show(2,4)
        if R.get(2, 4, 5):
            print "Get!"


if __name__ == '__main__':

    main()
