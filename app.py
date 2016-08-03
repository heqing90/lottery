"""

一、查询功能：当期开出的号，可以计算（显示）出遗漏的总和，篮球的遗漏不计算在内。
如本期开：1 2 3 4 5 6 遗漏和为3+1+0+4+16+6=30
二、选号功能：两个条件（1.遗漏和，2.号段内出的个数）
将号码分为三段 1-11；12-22；23-33（此号段先暂定，最好以后可修改，根据实际情况划分三个或四个号段）
选号程序设计为：2+3+1；3+2+1；2+2+2，（这个先定这个三个模式，后期最好可以随时调整）
2+3+1即号段1为2个数，号段2为3个数，号段3为1个数
举例：本期买遗漏和30，号段1内出6个数，一种可能就是1 2 3 4 5 6+X

"""

import random
import tkinter as tk
from tkinter import ttk
from tkinter import *
import urllib.request
import json
import os


class LotteryQurey(object):
    """docstring for LotteryQurey"""
    DB_FILE = os.path.join(os.path.dirname(__file__), 'lottery.json')
    QUERY_URL = 'http://f.apiplus.cn/ssq-50.json'
    DEFAULT_CODE = [num for num in range(1, 34)]

    def __init__(self):
        self._data = {}
        self.__load()

    def refresh(self):
        try:
            data = urllib.request.urlopen(self.QUERY_URL).read().decode('utf-8')
            data = json.loads(data)['data']
            self.__parse_data(data)
            self.__save()
        except Exception as e:
            raise e

    def __parse_data(self, data):
        lotteries = {}
        for item in data:
            lottery = {}
            lottery['expect'] = item['expect']
            # the last one is blue code.
            lottery['code'] = [int(num) for elem in item['opencode'].split(',') for num in (elem.split('+') if '+' in elem else [elem])]
            lottery['redcode'] = lottery['code'][:-1]
            lottery['bluecode'] = lottery['code'][-1]
            lottery['lostcode'] = list(set(self.DEFAULT_CODE) - set(lottery['redcode']))
            lotteries[lottery['expect']] = lottery
        self._data.update(lotteries)

    def __load(self):
        try:
            if os.path.exists(self.DB_FILE):
                with open(self.DB_FILE, 'r') as fd:
                    self._data = json.load(fd)
            else:
                # init data from internet
                self.refresh()
        except Exception as e:
            raise e

    def __save(self):
        try:
            if os.path.exists(self.DB_FILE):
                BK_FILE = '{file}.bk'.format(file=self.DB_FILE)
                if os.path.exists(BK_FILE):
                    os.remove(BK_FILE)
                os.rename(self.DB_FILE, BK_FILE)
            with open(self.DB_FILE, 'w') as fd:
                json.dump(self._data, fd)
        except Exception as e:
            raise e

    @property
    def data(self):
        return self._data

    @property
    def edition(self):
         tmp = [elem for elem in self._data]
         tmp.sort(reverse=True)
         return tmp


class App(object):
    def __init__(self):
        self.root = tk.Tk()
        self.style = ttk.Style()
        available_themes = self.style.theme_names()
        random_theme = random.choice(available_themes)
        # xpnative
        self.style.theme_use(random_theme)
        self.root.title('遗漏选号谦哥版')
        self.root.geometry('600x480+0+0')
        self._lottery = LotteryQurey()
        self.__initialize_components()

    def __initialize_components(self):
        try:
            self.__initialize_left()
            self.__initialize_right()
            self.__refresh_view()
        except Exception as e:
            raise e

    def __initialize_left(self):
        self.frm_left =tk.LabelFrame(self.root)
        self.frm_left.grid(row=0, column=0, padx=16)

        self.btn_refresh_data = tk.Button(self.frm_left, text='  刷新  ', command=self.__refresh_raw_data)
        self.btn_refresh_data.grid(row=0, column=1, padx=8, sticky=E)

        self.cbb_lottery_edition = StringVar()
        self.cbb_edition = ttk.Combobox(self.frm_left, textvariable=self.cbb_lottery_edition)
        self.cbb_edition['value'] = self._lottery.edition
        self.cbb_edition['state'] = 'readonly'
        self.cbb_edition.bind('<<ComboboxSelected>>', self.__edition_change)
        self.cbb_edition.grid(row=0,column=0, padx=8)
        self.cbb_edition.current(0)

        self.cbb_select_mode_var = StringVar()
        self.cbb_select_mode = ttk.Combobox(self.frm_left, textvariable=self.cbb_select_mode_var)
        self.cbb_select_mode['value'] = ['2-3-1', '3-2-1', '2-2-2']
        self.cbb_select_mode.grid(row=1,column=0, padx=8)
        self.cbb_select_mode.current(0)

        self.btn_select_code = tk.Button(self.frm_left, text='开始选号', command=self.__select_code)
        self.btn_select_code.grid(row=1, column=1)

    def __initialize_right(self):
        self.frm_right =tk.LabelFrame(self.root)
        self.frm_right.grid(row=0, column=1)

        self.lb_opencode = tk.Label(self.frm_right, text='开奖号码:')
        self.lb_opencode.grid(row=0, column=0, padx=8)

        self.tf_opencode_var = StringVar()
        self.tf_oepncode = tk.Entry(self.frm_right, textvariable=self.tf_opencode_var)
        self.tf_oepncode.grid(row=0, column=1, padx=8)

        self.lb_lostcode = tk.Label(self.frm_right, text='遗漏号码(合):')
        self.lb_lostcode.grid(row=1, column=0, padx=8)

        self.tf_lostcode_var = StringVar()
        self.tf_lostcode = tk.Entry(self.frm_right, textvariable=self.tf_lostcode_var)
        self.tf_lostcode.grid(row=1, column=1, padx=8)


    def __edition_change(self, event):
        print('edition changed!:{args}'.format(args=event))
        self.__refresh_view()

    def __get_current_lottery(self):
        edition = self.cbb_edition.get()
        lottery = self._lottery.data[edition]
        return lottery

    def __refresh_raw_data(self):
        print('refresh from internet')
        self._lottery.refresh()

    def __refresh_view(self):
        lottery = self.__get_current_lottery()
        self.tf_opencode_var.set(' '.join([repr(num) for num in lottery['code']]))
        lostcode = self.__calculate_lost_num()
        lost_code_str = ' '.join(['{num}({cnt})'.format(num=elem[0], cnt=elem[1]) for elem in lostcode])
        lost_code_sum_str = '合={sum}'.format(sum=sum([elem[1] for elem in lostcode]))
        self.tf_lostcode_var.set(','.join([lost_code_str, lost_code_sum_str]))

    def __calculate_lost_num(self):
        print('__calculate_lost_num')
        cur_edition = self.cbb_edition.get()
        lottery = self._lottery.data[cur_edition]
        all_edtion = self._lottery.edition
        lost_lottery_code = [[num, 0, False] for num in lottery['redcode']]
        is_find = False
        for item in all_edtion:
            if cur_edition == item:
                is_find = True
                continue
            elif is_find is True:
                for lostcode in lost_lottery_code:
                    if lostcode[0] in self._lottery.data[item]['redcode']:
                        lostcode[2] = True
                    else:
                        lostcode[1] += 1
            can_break = True
            for lostcode in lost_lottery_code:
                if lostcode[2] is False:
                    can_break = False
                    break
            if can_break is True:
                break
        print(lost_lottery_code)
        return lost_lottery_code

    def __select_code(self):
        print('start to select code')


app = App()
app.root.mainloop()
