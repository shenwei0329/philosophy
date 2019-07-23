#-*- coding: UTF-8 -*-
#
#   社会哲学体系
#   ============
#   Version 1.0
#
#   术语：
#   1）能量：唯一的度量
#   2）实体：社会组成基本元素，指具有核心（统治者）的组织化的人群，如部落、国家，是能力的获取和消耗者，若一个实体没有了能量，则表示被毁灭
#   3）环境：指大自然区域
#   4）资源：具有能量的对象，存在于环境和实体中
#   5）边界：实体之间，或实体与环境之间的边缘
#   6）渗透：在边界，当A的能量大于对方（如环境资源或对方实体）的能量时，边界向外扩张
#   7）吸收：在边界，A从环境资源吸收能量
#   8）吸引/诱惑：A总是朝向更有诱惑力的方向发展（如向更广的环境；向更弱的实体）
#   9）对抗：在边界，A与相邻实体之间能量的较量，边界能量与实体总能量成正比，与实体中心点到边界点的距离成反比
#   10）联盟：在边界，当A遇到比自己强的（对方总能量多于自己）实体时，寻求与相邻较弱实体结为联盟。结盟后，可合并能量，但不具备渗透能力
#
#   1）原始社会
#       面对大自然，求生存
#       原始社会是以亲族关系为基础，人口很少，经济生活采取平均主义分配办法，对社会的控制靠传统和家长来维系。
#

from curses_modules import basic
import time, random, sys


def main():

    random.seed(time.clock())
    scr = basic.Screen()

    try:
        scr.set_win()
        scr.refresh(force=True)

        scr.show_info("Press 'q' key to Quit...")

        while True:
            scr.refresh()
            time.sleep(0.01)
            _chr = scr.get_ch_and_continue(False)
            if _chr == ord('q'):
                scr.saveData()
                break
    except Exception, e:
        scr.get_ch_and_continue(True)
        raise e
    finally:
        scr.saveData()
        scr.unset_win()


if __name__ == '__main__':

    main()
