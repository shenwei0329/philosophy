#-*- coding: UTF-8 -*-
#
#   社会哲学体系
#   ============
#   Version 1.0
#
#   1）原始社会
#       面对大自然，求生存
#       原始社会是以亲族关系为基础，人口很少，经济生活采取平均主义分配办法，对社会的控制靠传统和家长来维系。
#

from curses_modules import basic,obj
import time, random, sys

edge_pattern = '^'
obj_pattern = ['.', '-', '=', '+', '#', 'x', '*', 'o', 'O']

def main():

    random.seed(time.clock())
    scr = basic.Screen()

    try:
        scr.set_win()
        scr.refresh(force=True, edge=edge_pattern)

        scr.show_info("Press 'q' key to Quit...")

        dot = []
        for _i in range(10):
            dot.append(obj.Obj("%d" % _i, 0, 0, obj_pattern[_i % len(obj_pattern)], (_i % 7)+1))
        while True:
            for _d in dot:
                _d.move()
                _x,_y,_cr,_col = _d.getPosition()
                scr.display_dot(_x,_y,_cr,colorpair=_col)
            scr.refresh(edge=edge_pattern)
            time.sleep(0.01)
            chr = scr.get_ch_and_continue(False)
            if chr==ord('q'):
                scr.saveData()
                for _d in dot:
                    _d.save()
                break
    except Exception,e:
        scr.get_ch_and_continue(True)
        raise e
    finally:
        scr.unset_win()

if __name__=='__main__':

    main()
