# -*- coding: utf-8 -*-
#
#   基类 Screen
#   ===========
#

import curses
import json

MENU_W = 40

class TimeScale:

    def __init__(self):
        self.TS = 0
        self.year = 0
        self.month = 0
        self.day = 0
        self._load('timescale.txt')

    def _save(self, fn):
        fp = open(fn, 'w')
        _ts = {
            'TS': self.TS,
            'year': self.year,
            'month': self.month,
            'day': self.day,
        }
        json.dump(_ts, fp)
        fp.close()

    def _load(self, fn):
        try:
            fp = open(fn, 'r')
            _ts = json.load(fp)
            self.TS = _ts['TS']
            self.year = _ts['year']
            self.month = _ts['month']
            self.day = _ts['day']
            fp.close()
        except:
            self.TS = 0
            self.year = 0
            self.month = 0
            self.day = 0
            self._save(fn)

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
        self._save('timescale.txt')

class Screen:

    def __init__(self):
        self.stdscr = curses.initscr()
        self.MAX_Y, self.MAX_X = self.stdscr.getmaxyx()
        self.window = self.stdscr.subwin(self.MAX_Y,self.MAX_X,0,0)
        self.main_window = self.window.subwin(self.MAX_Y-2,self.MAX_X-MENU_W-3,1,1)
        self.menu_window = self.window.subwin(self.MAX_Y-2,MENU_W,1,self.MAX_X-MENU_W-2)
        self._max_y = self.MAX_Y-4
        self._max_x = self.MAX_X-MENU_W-6
        self.screen = {}
        self.TS = TimeScale()
        self.loadData('screen.txt')

    def loadData(self, file_name):
        try:
            fp = open(file_name, 'r')
            _screen = json.load(fp)
            for _k in _screen:
                self.screen[int(_k)] = _screen[_k]
            fp.close()
        except:
            for _x in range(0, self._max_x):
                self.screen[_x] = []
                for _y in range(0, self._max_y):
                    self.screen[_x].append([_y, ' ', 0, False])

    def saveData(self):
        fp = open('screen.txt', 'w')
        json.dump(self.screen, fp)
        fp.close()

    def getX(self):
        return self._max_x

    def getY(self):
        return self._max_y

    def display_info(self, str, x, y, colorpair=2):

        if x<0:
            x = self._max_x - (x % self._max_x)
        else:
            x = (x % self._max_x)
            if x>0:
                x -= 1

        if y<0:
            y = self._max_y - (y % self._max_y)
        else:
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

    def refresh(self, force=False, edge='^'):

        self.TS.addTS()

        for _x in self.screen:
            for _y in self.screen[_x]:
                if self.isEdge(_x,_y[0],edge):
                    self.main_window.addstr(_y[0]+1, _x+1, edge, curses.color_pair(_y[2]) | curses.A_BOLD)
                elif force or _y[3]:
                    self.main_window.addstr(_y[0]+1, _x+1, _y[1], curses.color_pair(_y[2]) | curses.A_BOLD)
                    self.screen[_x][_y[0]][3] = False
        _t, _year, _month, _day = self.TS.getTS()
        self.menu_window.addstr(1, 2, "TimeScale: % 8d" % _t)
        self.menu_window.addstr(2, 2, "Date: % 6d-%02d-%02d" % (_year, _month+1, _day+1))
        self.main_window.refresh()
        self.menu_window.refresh()

    def get_ch_and_continue(self, wait):
        if wait:
            self.window.nodelay(0)
        self.window.nodelay(1)
        ch = self.window.getch()
        return ch

    def set_win(self):
        curses.start_color()
        curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_BLUE, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(7, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(10, curses.COLOR_BLACK, curses.COLOR_BLACK)
        curses.noecho()
        curses.cbreak()
        self.stdscr.nodelay(1)
        self.window.box()
        self.main_window.box()
        self.menu_window.box()

    def unset_win(self):
        self.TS.saveTS()
        curses.nocbreak()
        self.stdscr.keypad(0)
        curses.echo()
        curses.endwin()
