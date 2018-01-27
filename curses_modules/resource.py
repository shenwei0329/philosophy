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
#


import math, random, json, time

random.seed(time.time())

class E:
    """
    能量E
    """

    def __init__(self):
        self.max_quota = 10000
        self.quota = 10

    def dlt_E(self, time_scale):
        _x = (float(time_scale)/24.) % 360
        self.quota -= math.cos((2 * math.pi / 360) * _x)
        if self.quota<0:
            self.quota = 0
        elif self.quota>self.max_quota:
            self.quota = self.max_quota

    def show(self):
        return self.quota

    def get(self, e_quota):
        if self.quota>e_quota:
            self.quota-=e_quota
            return True
        else:
            return False

class Ps:
    """
    个人Ps
    """

    def __init__(self):
        self.quota = 10
        if random.random() > 0.5:
            self.sex = 'Male'
            self.dltQ = 8.
        else:
            self.sex = 'Female'
            self.dltQ = 5.
        self.day = 0
        self.age = 0

    def life_one_day(self):
        self.day += 1
        if (self.day % 90) == 0:
            self.age += 0.25
        """人对E的需要：【0-80岁】
        """
        self.quota += self.dltQ * math.sin((math.pi/80.)*self.age)
        return self.quota

    def show(self):
        return self.quota

    def alive(self):
        if (self.age/360.) > 80:
            return False
        else:
            return True

class Resource:

    def __init__(self, MAX_X, MAX_Y):
        self.MAX_X = MAX_X
        self.MAX_Y = MAX_Y
        self.E_unit = {}
        for _x in range(self.MAX_X):
            self.E_unit[_x] = []
            for _y in range(self.MAX_Y):
                self.E_unit[_x].append(E())

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

def main():

    R = Resource(50,50)
    for _i in range(0,365*20,10):
        R.refresh(_i)
        print R.show(2,4)
        if R.get(2,4,5):
            print "Get!"

if __name__=='__main__':

    main()
