# -*- coding: utf-8 -*-
#
#   基类 Screen
#   ===========
#

import curses
#import MySQLdb
import json
import types
import resource
import obj
from pymongo import MongoClient


MENU_W = 40
SEASON = ['Winter','Spring','Summer','Autumn']
MONTH_SEASON = [0, 0, 1, 1, 1, 2, 2, 2, 3, 3, 3, 0]
edge_pattern = '^'
obj_pattern = ['.', '-', '=', '+', '#', 'x', '*', 'o', 'O']

# def_backup = 'mongodb'
def_backup = 'none'

db = None
cur = None
if def_backup == 'mysql':
    """连接数据库"""
    db = MySQLdb.connect(host="127.0.0.1", user="root", passwd="sw64419", db="nebula", charset='utf8')
    cur = db.cursor()
elif def_backup == 'mongodb':
    db = MongoClient().philosophy


class SqlService:

    def __init__(self):
        global db, cur
        self.db = db
        self.cur = cur

    def insert(self, _sql):
        if self.cur is None:
            return
        try:
            self.cur.execute(_sql)
            self.db.commit()
        except:
            self.db.rollback()

    def count(self, _sql):
        if self.cur is None:
            return
        try:
            self.cur.execute(_sql)
            _result = self.cur.fetchone()
            _n = _result[0]
            if _n is None:
                _n = 0
        except:
            _n = 0
        finally:
            return _n

    def do(self, _sql):
        if self.cur is None:
            return
        self.cur.execute(_sql)
        return self.cur.fetchall()




class BackUp:
    """
    引入数据库操作：
    fn：主键
    data：值
    """

    def __init__(self, fn):
        global db,def_backup
        self.db = db
        self.fn = "data/%s" % fn
        self.key = fn
        self.sql_hdr = None
        if def_backup == 'mysql':
            self.sql_hdr = SqlService()

    def save(self, data):
        global def_backup

        try:
            if def_backup == 'mongodb':
                _data = json.dumps(data)
                if type(self.db.info.find_one({"key": self.key})) is types.NoneType:
                    self.db.info.insert({"key": self.key, "value": _data})
                else:
                    self.db.info.update({"key": self.key}, {"key": self.key, "value": _data})
            elif def_backup == 'file':
                fp = open(self.fn, 'w')
                json.dump(data, fp)
                fp.close()
            else:
                _str = json.dumps(data)
                _sql = 'select id from backup_t where key="%s"' % self.key
                if self.sql_hdr.count(_sql)>0:
                    _sql = 'update backup_t set value="%s" where key="%s"' % (_str, self.key)
                    self.sql_hdr.do(_sql)
                else:
                    _sql = 'insert into backup_t(key,value) values("%s","%s")' % (_str, self.key)
                    self.sql_hdr.insert(_sql)
        except:
            return

    def load(self):
        global def_backup
        try:
            if def_backup == 'file':
                fp = open(self.fn, 'r')
                _data = json.load(fp)
                fp.close()
            elif def_backup == 'mongodb':
                _data = self.db.info.find_one({"key": self.key})
                if type(_data) is not types.NoneType:
                    _data = json.loads(_data["value"])
            else:
                _sql = 'select value from backup_t where key="%s"' % self.key
                _res = self.sql_hdr.do(_sql)
                if (_res is not None) and (len(_res) > 0):
                    _data = _res[0]
                else:
                    _data = None
            return _data
        except:
            return None


class TimeScale:

    def __init__(self):
        self.backup = BackUp("timescale")
        self.TS = 0
        self.year = 0
        self.month = 0
        self.day = 0
        self._load()

    def _save(self):
        _ts = {
            'TS': self.TS,
            'year': self.year,
            'month': self.month,
            'day': self.day,
        }
        self.backup.save(_ts)

    def _load(self):
        _ts = self.backup.load()
        if _ts is not None:
            self.TS = _ts['TS']
            self.year = _ts['year']
            self.month = _ts['month']
            self.day = _ts['day']
        else:
            self.TS = 0
            self.year = 0
            self.month = 0
            self.day = 0
            self._save()

    def getTS(self):
        return self.TS, self.year, self.month, self.day

    def addTS(self):
        self.TS += 1
        if (self.TS % 24) == 0:
            self.day += 1
            if self.day == 30:
                self.day = 0
                self.month += 1
                if self.month == 12:
                    self.month = 0
                    self.year += 1

    def saveTS(self):
        self._save()


class Screen:

    def __init__(self):
        self.backup = BackUp("screen")
        self.stdscr = curses.initscr()
        self.MAX_Y, self.MAX_X = self.stdscr.getmaxyx()
        self.window = self.stdscr.subwin(self.MAX_Y,self.MAX_X,0,0)
        self.main_window = self.window.subwin(self.MAX_Y-2,self.MAX_X-MENU_W-3,1,1)
        self.menu_window = self.window.subwin(self.MAX_Y-2,MENU_W,1,self.MAX_X-MENU_W-2)
        self._max_y = self.MAX_Y-4
        self._max_x = self.MAX_X-MENU_W-6
        self.screen = {}
        """创建【时标】
        """
        self.TS = TimeScale()
        """创建【资源】
        """
        self.R = resource.Resource(self._max_x,self._max_y)
        self.loadData()
        """创建【对象】
        """
        self.Obj = []
        for _i in range(5):
            self.Obj.append(obj.Obj("%d" % _i, 0, 0, obj_pattern[_i % len(obj_pattern)], (_i % 7)+1))

    def set_power(self, e, total_power):
        """按比例分配能量"""
        _sum = 0
        """计算资源总数"""
        for _en in e:
            _sum += e[_en]

        _ret = {}
        for _o in self.Obj:
            _p = _o.get_chr()
            if _p in e:
                _ret[_p] = float(e[_p])/float(_sum)
                _o.set_power(int(float(total_power)*_ret[_p]))
        return _ret

    def loadData(self):
        _screen = self.backup.load()
        if _screen is not None:
            for _k in _screen:
                self.screen[int(_k)] = _screen[_k]
        else:
            for _x in range(0, self._max_x+1):
                self.screen[_x] = []
                for _y in range(0, self._max_y):
                    self.screen[_x].append([_y, ' ', 0, False])

    def saveData(self):
        self.backup.save(self.screen)
        for _o in self.Obj:
            _o.save()


    def getX(self):
        return self._max_x

    def getY(self):
        return self._max_y

    def display_info(self, str, x, y, colorpair=2):

        if x<0:
            x = self._max_x - (x % self._max_x)
        x = (x % self._max_x)
        if x>0:
            x -= 1

        if y<0:
            y = self._max_y - (y % self._max_y)
        y = (y % self._max_y)
        if y>0:
            y -= 1

        if self.screen[x][y][1] != str or self.screen[x][y][2] != colorpair:
            self.screen[x][y][1] = str
            self.screen[x][y][2] = colorpair
            self.screen[x][y][3] = True

    def show_info(self, str):
        self.display_info(str, self._max_x/2, self._max_y-1)

    def clr_dot(self, x, y):
        self.display_info(' ', x, y, colorpair=10)

    def display_dot(self, x, y, chr, colorpair=2):
        self.display_info(chr, x, y, colorpair=colorpair)

    def debug(self, str):
        self.window.addstr(self._max_y-1, 2, str, curses.color_pair(3))

    def isEdge(self,x,y,edge):

        _ch = self.screen[x][y][1][0]

        _ch_N = _ch
        _ch_W = _ch
        _ch_S = _ch
        _ch_E = _ch

        if y > 0:
            _ch_N = self.screen[x][y-1][1][0]

        if x > 0:
            _ch_W = self.screen[x-1][y][1][0]

        if y < self._max_y-1:
            _ch_S = self.screen[x][y+1][1][0]

        if x < self._max_x-1:
            _ch_E = self.screen[x+1][y][1][0]

        if (_ch != _ch_N) or (_ch != _ch_E) or (_ch != _ch_W) or (_ch != _ch_S):
            return True
        return False

    def refresh(self, force=False):

        edge = edge_pattern
        self.TS.addTS()
        _t, _year, _month, _day = self.TS.getTS()
        """更新【资源】
        """
        _total_E = self.R.refresh(_t)

        """扫描“领地”"""
        _counter = {}
        for _x in self.screen:
            for _y in self.screen[_x]:
                if self.isEdge(_x, _y[0], edge):
                    self.main_window.addstr(_y[0]+1, _x+1, edge, curses.color_pair(_y[2]) | curses.A_BOLD)
                elif force or _y[3]:
                    self.main_window.addstr(_y[0]+1, _x+1, _y[1], curses.color_pair(_y[2]) | curses.A_BOLD)
                    self.screen[_x][_y[0]][3] = False
                if _y[1] not in _counter:
                    _counter[_y[1]] = 0
                _counter[_y[1]] += 1

        _rat = self.set_power(_counter, _total_E)

        """显示当前状态
        """
        self.menu_window.addstr(1, 2, "TimeScale: % 8d" % _t)
        self.menu_window.addstr(2, 2, "Date: % 6d-%02d-%02d " % (_year, _month+1, _day+1))
        _season = MONTH_SEASON[_month]
        self.menu_window.addstr(2, 22, "%s" % SEASON[_season], curses.color_pair(_season) | curses.A_BOLD)
        self.menu_window.addstr(3, 2, "Total E:    % 12d" % _total_E, curses.color_pair(_season) | curses.A_BOLD)

        _i = 0
        _tot_alive = 0
        _tot_req = 0
        for _o in self.Obj:
            _o.move()
            _alive, _req, _male, _female, _mating = _o.time_scale(_t)
            _tot_alive += _alive
            _tot_req += _req
            _x, _y, _cr, _col = _o.getPosition()
            self.display_dot(_x, _y, _cr, colorpair=_col)
            # _x, _y, _cr, _col = _o.getPosition()
            if _o.get_chr() in _counter:
                self.menu_window.addstr(7+_i*3, 2, "Obj[%c%d]:%05d %0.2f" % (_cr,
                                                                             _col,
                                                                             _counter[_o.get_chr()],
                                                                             _rat[_o.get_chr()]
                                                                             ))
            self.menu_window.addstr(8+_i*3, 4, "% 6d % 8d % 5d % 5d % 5d" % (_alive, _req, _male, _female, _mating),
                                    curses.color_pair(7) | curses.A_BOLD)
            _i += 1
        self.menu_window.addstr(4, 2, "Total P:    % 12d" % _tot_alive, curses.color_pair(1) | curses.A_BOLD)
        self.menu_window.addstr(5, 2, "Total Ereq: % 12d" % _tot_req, curses.color_pair(7) | curses.A_BOLD)
        self.main_window.refresh()
        self.menu_window.refresh()

    def get_ch_and_continue(self, wait):
        if wait:
            self.stdscr.nodelay(0)
        ch = self.stdscr.getch()
        self.stdscr.nodelay(1)
        return ch

    def set_win(self):
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(7, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(8, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(10, curses.COLOR_BLACK, curses.COLOR_BLACK)
        curses.noecho()
        curses.cbreak()
        self.stdscr.nodelay(1)
        self.window.box()
        self.main_window.box()
        self.menu_window.box()

    def unset_win(self):
        self.TS.saveTS()
        self.R.save()
        curses.nocbreak()
        self.stdscr.keypad(0)
        curses.echo()
        curses.endwin()
