# -*- coding=utf8 -*-

"""
V1.
一、查询功能：当期开出的号，可以计算（显示）出遗漏的总和，篮球的遗漏不计算在内。
如本期开：1 2 3 4 5 6 遗漏和为3+1+0+4+16+6=30
二、选号功能：两个条件（1.遗漏和，2.号段内出的个数）
将号码分为三段 1-11；12-22；23-33（此号段先暂定，最好以后可修改，根据实际情况划分三个或四个号段）
选号程序设计为：2+3+1；3+2+1；2+2+2，（这个先定这个三个模式，后期最好可以随时调整）
2+3+1即号段1为2个数，号段2为3个数，号段3为1个数
举例：本期买遗漏和30，号段1内出6个数，一种可能就是1 2 3 4 5 6+X

V2

条件1： 选号区间设定：1-3-2；2-2-2（如果此设置不是很复杂，可以加上1-2-3和2-3-1）
条件2：遗漏和值区间
条件3：与上期开奖号最大重复数（0、1、2）
条件4：允许出现连号的号码0/1组，1组即2个号，3连号以上排除。
条件5：奇偶比设定（2:4,3:3,4:2）

"""

import json
import os
import random
import sys
from itertools import combinations

print(sys.version)
PY2X = sys.version_info[0] == 2
import Tkinter as tk
import tkMessageBox as tkmsgbox
import ttk
from Tkinter import *
import urllib2


class LotteryQurey(object):
    """docstring for LotteryQurey"""
    DB_FILE = os.path.join(os.path.dirname(__file__), 'lottery.json')
    DB_SELECTED_FILE = os.path.join(os.path.dirname(__file__), 'last_selected.json')
    QUERY_URL_163 = 'http://trend.caipiao.163.com/ssq/historyPeriod.html?periodNumber=100'
    DEFAULT_CODE = [num for num in range(1, 34)]

    def __init__(self):
        self._data = {}
        self._selected_codes = []
        self.__load()

    def refresh(self):
        try:
            data = self.__get_data_163()
            self.__parse_data(data)
            self.__save()
        except Exception as e:
            print('ERROR: cannot get the new info from internet.[{err}]'.format(err=e))

    def __get_data_163(self):
        try:
            html = urllib2.urlopen(self.QUERY_URL_163).read().decode('utf-8')
            p = re.compile('data-period=\"(.*)\" data-award=\"(.*)\"')
            codes = p.findall(html)
            # print codes
            data = []
            for code in codes:
                # print code
                expect = code[0]
                red_code = code[1].split(':')[0]
                blue_code = code[1].split(':')[1]
                item = {'expect': expect, 'redcode': red_code, 'bluecode': blue_code}
                data.append(item)
            return data
        except Exception as e:
            print ('ERROR: cannot get the data from 163.com. {}'.format(e))

    def save_selected_codes(self, seleced_codes):
        try:
            save_data = {'last_selected': seleced_codes}
            self._selected_codes = list(seleced_codes)
            with open(self.DB_SELECTED_FILE, 'w') as fd:
                json.dump(save_data, fd)
        except Exception as e:
            print('ERROR: Cannot save seleted codes! {}'.format(e))

    def __parse_data(self, data):
        lotteries = {}
        try:
            for item in data:
                lottery = {'expect': item['expect'], 'redcode': [int(num) for num in item['redcode'].split()],
                           'bluecode': int(item['bluecode'])}
                lotteries[lottery['expect']] = lottery
            self._data.update(lotteries)
        except Exception as e:
            print('ERROR: Cannot save parse codes!{}'.format(e))

    def __load(self):
        try:
            if os.path.exists(self.DB_FILE):
                with open(self.DB_FILE, 'r') as fd:
                    self._data = json.load(fd)
            # update data from internet
            self.refresh()
            if os.path.exists(self.DB_SELECTED_FILE):
                with open(self.DB_SELECTED_FILE, 'r') as fd:
                    save_data = json.load(fd)
                    self._selected_codes = save_data.get('last_selected', [])
        except Exception as e:
            print('ERROR: cannot get the new info from local.[{err}]'.format(err=e))

    def __save(self):
        try:
            if os.path.exists(self.DB_FILE):
                back_file = '{file}.bk'.format(file=self.DB_FILE)
                if os.path.exists(back_file):
                    os.remove(back_file)
                os.rename(self.DB_FILE, back_file)
            with open(self.DB_FILE, 'w') as fd:
                json.dump(self._data, fd, indent=4, separators=(',', ': '))
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

    @property
    def allcode(self):
        return self.DEFAULT_CODE

    @property
    def selectedcodes(self):
        return self._selected_codes


class CombinationsTool(object):
    @classmethod
    def get(cls, select_mode, open_code, all_lost_code, min_lost, max_lost, repeat_cnt, repeat_team_max_cnt, odd_cnt,
            min_opensum, max_opensum, contains_codes):
        """
        :param select_mode:
        :param open_code:
        :param all_lost_code:
        :param min_lost:
        :param max_lost:
        :param repeat_cnt:
        :param repeat_team_max_cnt:
        :param odd_cnt:
        :param min_opensum:
        :param max_opensum:
        :param contains_codes:
        :return:
        """
        tmp = select_mode.split('-')
        low_code_cnt, mid_code_cnt, high_code_cnt = int(tmp[0]), int(tmp[1]), int(tmp[2])
        low_code = [num[0] for num in all_lost_code if num[1] < max_lost and num[0] in range(1, 12)]
        mid_code = [num[0] for num in all_lost_code if num[1] < max_lost and num[0] in range(12, 23)]
        high_code = [num[0] for num in all_lost_code if num[1] < max_lost and num[0] in range(23, 34)]

        low_code_ret = cls.__calculate(low_code, low_code_cnt)
        mid_code_ret = cls.__calculate(mid_code, mid_code_cnt)
        high_code_ret = cls.__calculate(high_code, high_code_cnt)

        results = []
        for high in high_code_ret:
            for low in low_code_ret:
                for mid in mid_code_ret:
                    tmp_high = list(high)
                    tmp_low = list(low)
                    tmp_mid = list(mid)
                    calculate_arr = []
                    calculate_arr.extend(tmp_low)
                    calculate_arr.extend(tmp_mid)
                    calculate_arr.extend(tmp_high)
                    lost_sum = sum([all_lost_code[elem - 1][1] for elem in calculate_arr])
                    calculate_arr.sort()
                    if len(contains_codes) > 0:
                        if len(set(contains_codes) & set(calculate_arr)) != len(contains_codes):
                            continue
                    is_continue = False
                    repeat_team_cnt = 0
                    for index in range(5):
                        serial_arr = list(range(calculate_arr[index], calculate_arr[index] + 3))
                        repeat_count = len(set(serial_arr) & set(calculate_arr))
                        if repeat_count > 2:
                            # ignore more than 3 chains number
                            is_continue = True
                            break
                        elif repeat_count > 1:
                            serial_arr = list(range(calculate_arr[index], calculate_arr[index] + 2))
                            repeat_count = len(set(serial_arr) & set(calculate_arr))
                            if repeat_count == 2:
                                repeat_team_cnt += 1
                    if is_continue is True or repeat_team_cnt != repeat_team_max_cnt:
                        continue
                    if odd_cnt > -1:
                        odd_numbers = [num for num in calculate_arr if num % 2 != 0]
                        if len(odd_numbers) != odd_cnt:
                            continue
                    if max_opensum != 0 and (sum(calculate_arr) < min_opensum or sum(calculate_arr) > max_opensum):
                        continue
                    if min_lost <= lost_sum <= max_lost and \
                            len(set(calculate_arr) & set(open_code)) <= repeat_cnt:
                        results.append([calculate_arr, lost_sum])
        return results

    @classmethod
    def __calculate(cls, arr, cnt):
        return list(combinations(arr, cnt))


class App(object):
    DB_SELECTED_CONF_FILE = os.path.join(os.path.dirname(__file__), 'select_conf.json')

    @classmethod
    def main(cls):
        root = tk.Tk()
        root.grid_columnconfigure(0, weight=1)
        style = ttk.Style()
        available_themes = style.theme_names()
        random_theme = random.choice(available_themes)
        style.theme_use(random_theme)
        root.title('遗漏选号谦哥版')
        w = 1200
        h = 780
        root.geometry("%dx%d" % (w, h))
        app = cls(root)
        root.protocol("WM_DELETE_WINDOW", app.__on_closing_window)
        root.mainloop()

    def __init__(self, root):
        self.root = root
        self._lottery = LotteryQurey()
        self.__initialize_components()
        self.__load_select_conf()

    def __initialize_components(self):
        try:
            self.__initialize_left()
            self.__initialize_right()
            self.__initialize_right_bottom()
            self.__load_local_data()
            self.__refresh_view()
        except Exception as e:
            raise e

    def __initialize_left(self):
        self.frm_left = tk.LabelFrame(self.root)
        self.frm_left.pack(side=LEFT, fill=Y, padx=4)

        self.cbb_lottery_edition = StringVar()
        self.cbb_edition = ttk.Combobox(self.frm_left, textvariable=self.cbb_lottery_edition)
        self.cbb_edition['value'] = self._lottery.edition
        self.cbb_edition['state'] = 'readonly'
        self.cbb_edition.bind('<<ComboboxSelected>>', self.__edition_change)
        # self.cbb_edition.grid(row=0, column=0, padx=8, sticky=W)
        self.cbb_edition.pack(fill=X, pady=8)
        self.cbb_edition.current(0)

        self.btn_refresh_data = tk.Button(self.frm_left, text='手 动 刷 新', font='16', bg='PaleGreen',
                                          command=self.__refresh_raw_data)
        self.btn_refresh_data.pack(fill=X, pady=8)

        self.lb_select_mode = tk.Label(self.frm_left, anchor=W, text='区间比(可输入 低区-中区-高区)')
        self.lb_select_mode.pack(fill=X)

        self.cbb_select_mode_var = StringVar()
        self.cbb_select_mode = ttk.Combobox(self.frm_left, textvariable=self.cbb_select_mode_var)
        self.cbb_select_mode['value'] = ['2-3-1', '3-2-1', '2-2-2', '1-2-3', '1-3-2', '3-1-2']
        self.cbb_select_mode.pack(fill=X, pady=8)
        self.cbb_select_mode.current(0)

        self.lb_select_mode = tk.Label(self.frm_left, anchor=W, text='奇偶比(可输入 奇数-偶数)')
        self.lb_select_mode.pack(fill=X)

        self.cbb_select_odd_var = StringVar()
        self.cbb_select_odd = ttk.Combobox(self.frm_left, textvariable=self.cbb_select_odd_var)
        self.cbb_select_odd['value'] = ['2-4', '4-2', '1-5', '5-1', '3-3']
        self.cbb_select_odd.pack(fill=X, pady=8)
        self.cbb_select_odd.current(0)

        self.ckb_is_allow_odd_var = BooleanVar()
        self.ckb_is_allow_odd = tk.Checkbutton(
            self.frm_left,
            text='是否允许奇偶比',
            font='12',
            anchor=W,
            variable=self.ckb_is_allow_odd_var,
            onvalue=True,
            offvalue=False)
        self.ckb_is_allow_odd.pack(fill=X, pady=8)

        self.lb_opencode = tk.Label(self.frm_left, text='遗漏区间(25~35)')
        self.lb_opencode.pack()
        self.frm_left_lost_range = tk.LabelFrame(self.frm_left)
        self.frm_left_lost_range.pack()
        self.tf_range_min_var = StringVar()
        self.tf_range_min = tk.Entry(self.frm_left_lost_range, justify=CENTER, textvariable=self.tf_range_min_var)
        self.tf_range_min.pack(side=LEFT)
        self.lb_opencode = tk.Label(self.frm_left_lost_range, text='~~~')
        self.lb_opencode.pack(side=LEFT)
        self.tf_range_max_var = StringVar()
        self.tf_range_max = tk.Entry(self.frm_left_lost_range, justify=CENTER, textvariable=self.tf_range_max_var)
        self.tf_range_max.pack(side=LEFT)
        self.tf_range_min_var.set('25')
        self.tf_range_max_var.set('35')

        self.lb_opencode_sum = tk.Label(self.frm_left, text='开奖和值区间(0~0表示不启用))')
        self.lb_opencode_sum.pack()
        self.frm_left_opensum_range = tk.LabelFrame(self.frm_left)
        self.frm_left_opensum_range.pack()
        self.tf_range_sum_min_var = IntVar()
        self.tf_range_sum_min = tk.Entry(self.frm_left_opensum_range, justify=CENTER,
                                         textvariable=self.tf_range_sum_min_var)
        self.tf_range_sum_min.pack(side=LEFT)
        self.lb_opencode_sum = tk.Label(self.frm_left_opensum_range, text='~~~')
        self.lb_opencode_sum.pack(side=LEFT)
        self.tf_range_sum_max_var = IntVar()
        self.tf_range_sum_max = tk.Entry(self.frm_left_opensum_range, justify=CENTER,
                                         textvariable=self.tf_range_sum_max_var)
        self.tf_range_sum_max.pack(side=LEFT)
        self.tf_range_sum_min_var.set('0')
        self.tf_range_sum_max_var.set('0')

        self.lb_repeat_cnt = tk.Label(self.frm_left, text='和本期开奖号码最大重复数:')
        self.lb_repeat_cnt.pack()
        self.tf_repeat_cnt_var = StringVar()
        self.tf_repeat_cnt = tk.Entry(self.frm_left, justify=CENTER, textvariable=self.tf_repeat_cnt_var)
        self.tf_repeat_cnt.pack(fill=X)
        self.tf_repeat_cnt_var.set('2')

        self.lb_contains_codes = tk.Label(self.frm_left, text='必含号码(多个用空格区分 1 2 3)')
        self.lb_contains_codes.pack()
        self.tf_contains_codes_var = StringVar()
        self.tf_contains_codes = tk.Entry(self.frm_left, justify=CENTER, textvariable=self.tf_contains_codes_var)
        self.tf_contains_codes.pack(fill=X)

        self.lb_opencode = tk.Label(self.frm_left, text='允许连号组数(3个以上连号排除)')
        self.lb_opencode.pack()

        self.frm_left_lost_repeat = tk.LabelFrame(self.frm_left)
        self.frm_left_lost_repeat.pack(fill=X, padx=8)
        self.rb_lost_repeat_cnt = IntVar()
        self.rb_lost_repeat_0 = tk.Radiobutton(self.frm_left_lost_repeat, text="0组", variable=self.rb_lost_repeat_cnt,
                                               value=0)
        self.rb_lost_repeat_1 = tk.Radiobutton(self.frm_left_lost_repeat, text="1组", variable=self.rb_lost_repeat_cnt,
                                               value=1)
        self.rb_lost_repeat_2 = tk.Radiobutton(self.frm_left_lost_repeat, text="2组", variable=self.rb_lost_repeat_cnt,
                                               value=2)
        self.rb_lost_repeat_3 = tk.Radiobutton(self.frm_left_lost_repeat, text="3组", variable=self.rb_lost_repeat_cnt,
                                               value=3)
        self.rb_lost_repeat_0.pack(side=LEFT, fill=X, expand=True)
        self.rb_lost_repeat_1.pack(side=LEFT, fill=X, expand=True)
        self.rb_lost_repeat_2.pack(side=LEFT, fill=X, expand=True)
        self.rb_lost_repeat_3.pack(side=LEFT, fill=X, expand=True)

        self.btn_select_code = tk.Button(self.frm_left, text='清空已选记录', font='16', fg='DarkOrange', bg='RoyalBlue',
                                         command=self.__clear_select_code)
        self.btn_select_code.pack(fill=X, pady=8)

        self.btn_select_code = tk.Button(self.frm_left, text='开 始 选 号', font='16', bg='Orange',
                                         command=self.__select_code)
        self.btn_select_code.pack(fill=X, pady=8)

        self.btn_save_select_code = tk.Button(self.frm_left, text='保 存 结 果', font='16', bg='FireBrick',
                                              command=self.__save_select_code)
        self.btn_save_select_code.pack(fill=X, pady=8)

    def __initialize_right(self):
        self.frm_right = tk.LabelFrame(self.root)
        self.frm_right.pack(fill=BOTH, expand=True)

        self.lb_opencode = tk.Label(self.frm_right, text='开奖号码:')
        self.lb_opencode.pack()

        self.tf_opencode_var = StringVar()
        self.tf_oepncode = tk.Entry(self.frm_right, justify=CENTER, font='Arial 16', fg='OrangeRed2', bg='ghost white',
                                    textvariable=self.tf_opencode_var)
        self.tf_oepncode['state'] = 'readonly'
        self.tf_oepncode.pack(fill=X)

        self.lb_curr_all_lostcode = tk.Label(self.frm_right, text='本期全号遗漏:')
        self.lb_curr_all_lostcode.pack()
        self.tf_curr_all_lostcode_var = StringVar()
        self.tf_curr_all_lostcode = tk.Entry(self.frm_right, justify=CENTER, font='Arial 10', fg='HotPink',
                                             bg='ghost white', textvariable=self.tf_curr_all_lostcode_var)
        self.tf_curr_all_lostcode['state'] = 'readonly'
        self.tf_curr_all_lostcode.pack(fill=X)

        self.lb_lostcode_var = StringVar()
        self.lb_lostcode = tk.Label(self.frm_right, textvariable=self.lb_lostcode_var)
        self.lb_lostcode.pack(fill=X)
        self.tf_lostcode_var = StringVar()
        self.tf_lostcode = tk.Entry(self.frm_right, justify=CENTER, font='Arial 16', fg='SteelBlue', bg='ghost white',
                                    textvariable=self.tf_lostcode_var)
        self.tf_lostcode['state'] = 'readonly'
        self.tf_lostcode.pack(fill=X)

        self.lb_selectcode_var = StringVar()
        self.lb_selectcode = tk.Label(self.frm_right, anchor=W, textvariable=self.lb_selectcode_var)
        self.lb_selectcode.pack(fill=X)
        self.lb_selectcode_var.set('选号结果: ')

    def __initialize_right_bottom(self):
        self.frm_right_bottom = tk.LabelFrame(self.frm_right)
        self.frm_right_bottom.pack(fill=BOTH, expand=True)

        self.list_selectcode = tk.Listbox(self.frm_right_bottom, font='Times 16', fg='forest green',
                                          selectmode=EXTENDED)
        self.sb_selectcode = tk.Scrollbar(self.frm_right_bottom, orient=VERTICAL)
        self.list_selectcode.config(yscrollcommand=self.sb_selectcode.set)
        self.sb_selectcode.config(command=self.list_selectcode.yview)
        self.list_selectcode.pack(side=LEFT, fill=BOTH, expand=True)
        self.sb_selectcode.pack(side=LEFT, fill=Y)
        self.list_selectcode.bind('<Control-a>', self.__select_all_electcodes)
        self.list_selectcode.bind('<Double-Button-1>', self.__doubleclick_on_selectcods_list)
        self.list_selectcode.bind('<space>', self.__doubleclick_on_selectcods_list)

        self.list_selectcode_out = tk.Listbox(self.frm_right_bottom, font='Arial  14', fg='goldenrod1',
                                              bg='white smoke', selectmode=EXTENDED)
        self.sb_selectcode_out = tk.Scrollbar(self.frm_right_bottom, orient=VERTICAL)
        self.list_selectcode_out.config(yscrollcommand=self.sb_selectcode_out.set)
        self.sb_selectcode_out.config(command=self.list_selectcode_out.yview)
        self.list_selectcode_out.pack(side=LEFT, fill=BOTH, expand=True)
        self.sb_selectcode_out.pack(side=LEFT, fill=Y)
        self.list_selectcode_out.bind('<Control-a>', self.__select_all_electcodes_out)
        self.list_selectcode_out.bind('<Double-Button-1>', self.__doubleclick_on_selectcodes_out_list)
        self.list_selectcode_out.bind('<space>', self.__doubleclick_on_selectcodes_out_list)
        self.list_selectcode_out.bind('<BackSpace>', self.__delete_on_selectcodes_out_list)
        self.list_selectcode_out.bind('<Control-v>', self.__paste_selectedcodes_out)
        self.list_selectcode_out.bind('<Control-d>', self.__delete_bingo_selected_codes)

    def __edition_change(self, event):
        self.__refresh_view()

    def __get_current_lottery(self):
        edition = self.cbb_edition.get()
        lottery = self._lottery.data[edition]
        return lottery

    def __refresh_raw_data(self):
        self._lottery.refresh()

    def __load_local_data(self):
        for item in self._lottery.selectedcodes:
            self.list_selectcode_out.insert(END, item)

    def __refresh_view(self):
        lostcode = self.__calculate_lost_current()
        lost_code_str = '  '.join(['{num}({cnt})'.format(num=elem[0], cnt=elem[1]) for elem in lostcode])
        lost_code_sum_str = '合={sum}({lostsum})'.format(sum=sum([elem[0] for elem in lostcode]),
                                                        lostsum=sum([elem[1] for elem in lostcode]))
        self.tf_opencode_var.set(','.join([lost_code_str, lost_code_sum_str]))
        # show lottery
        self.__refresh_bingo_selectedcodes_tips()
        self.__refresh_selection_results_tips()

    def __refresh_bingo_selectedcodes_tips(self):
        lvl_3_cnt = 0
        lvl_4_cnt = 0
        lvl_5_cnt = 0
        lvl_6_cnt = 0
        cur_lottery_codes = self.__get_current_opencode()
        index = 0
        for selected_code_str in self._lottery.selectedcodes:
            selected_code = [int(num) for num in (selected_code_str.split())]
            if len(set(cur_lottery_codes) & set(selected_code)) == 6:
                lvl_6_cnt += 1
                self.list_selectcode_out.itemconfig(index, {'bg': 'FireBrick', "fg": 'Black'})
            elif len(set(cur_lottery_codes) & set(selected_code)) == 5:
                lvl_5_cnt += 1
                self.list_selectcode_out.itemconfig(index, {'bg': 'DarkGoldenrod', "fg": 'Black'})
            elif len(set(cur_lottery_codes) & set(selected_code)) == 4:
                lvl_4_cnt += 1
                self.list_selectcode_out.itemconfig(index, {'bg': 'SteelBlue', "fg": 'Black'})
            elif len(set(cur_lottery_codes) & set(selected_code)) == 3:
                lvl_3_cnt += 1
                self.list_selectcode_out.itemconfig(index, {'bg': 'SeaGreen', "fg": 'Black'})
            else:
                self.list_selectcode_out.itemconfig(index, {'bg': 'white smoke', "fg": 'goldenrod1'})
            index += 1
        self.lb_lostcode_var.set('上期中奖结果(共 {cnt} 注)'.format(cnt=sum([lvl_3_cnt, lvl_4_cnt, lvl_5_cnt, lvl_6_cnt])))
        show_str = '中6球 [{cnt_6}] 注<红色>, 中5球 [{cnt_5}] 注<黄色>, 中4球 [{cnt_4}] 注<蓝色>, 中3球 [{cnt_3}] 注<绿色>'.format(
            cnt_6=lvl_6_cnt,
            cnt_5=lvl_5_cnt,
            cnt_4=lvl_4_cnt,
            cnt_3=lvl_3_cnt)
        self.tf_lostcode_var.set(show_str)
        lostcode = self.__calculate_lost_all()
        lost_code_str = '  '.join(['{num}({cnt})'.format(num=elem[0], cnt=elem[1]) for elem in lostcode])
        lost_code_sum_str = '合={sum}'.format(sum=sum([elem[1] for elem in lostcode]))
        self.tf_curr_all_lostcode_var.set(','.join([lost_code_str, lost_code_sum_str]))

    def __get_last_20_repeat_selected_lottery(self):
        bingo_codes_indexs = []
        editions = self._lottery.edition[:20]
        lotteries = [self._lottery.data[item]['redcode'] for item in editions]
        index = 0
        for selected_code_str in self._lottery.selectedcodes:
            selected_code = [int(num) for num in (selected_code_str.split())]
            if any(len(set(selected_code) & set(lottery)) > 2 for lottery in lotteries):
                bingo_codes_indexs.append(index)
            index += 1
        return bingo_codes_indexs

    def __refresh_selection_results_tips(self):
        cnt = self.list_selectcode.size()
        selected_cnt = self.list_selectcode_out.size()
        self.lb_selectcode_var.set(
            '选号结果: 共 {count} 注, 已选取 {selectedcnt} 注.(双击选中或选中+空格，可以(反)选取号码), 退格键(BackSpace)可删除已选, Ctrl+d删除与近20期重复3个号码以上'.format(
                count=cnt, selectedcnt=selected_cnt))

    def __calculate_lost_current(self):
        return self.__calculate_lost_code(self.__get_current_opencode(), is_cur_lost=True)

    def __get_current_opencode(self):
        cur_edition = self.cbb_edition.get()
        lottery = self._lottery.data[cur_edition]
        return lottery['redcode']

    def __calculate_lost_all(self):
        return self.__calculate_lost_code(self._lottery.allcode)

    def __calculate_lost_code(self, lost_code, spec_editon=None, is_cur_lost=False):
        if spec_editon is None:
            cur_edition = self.cbb_edition.get()
        else:
            cur_edition = spec_editon
        all_edtion = self._lottery.edition
        lost_lottery_code = [[num, 0, False] for num in lost_code]
        is_find = False
        for item in all_edtion:
            if cur_edition == item:
                is_find = True
                if is_cur_lost:
                    continue
            if is_find is True:
                for lostcode in lost_lottery_code:
                    if lostcode[2] is True:
                        continue
                    if lostcode[0] in self._lottery.data[item]['redcode']:
                        lostcode[2] = True
                    else:
                        lostcode[1] += 1
            else:
                continue
            can_break = True
            for lostcode in lost_lottery_code:
                if lostcode[2] is False:
                    can_break = False
                    break
            if can_break is True:
                break
        return lost_lottery_code

    @staticmethod
    def __codes_to_lottery(codes):
        return '  '.join(['{0:0>2}'.format(elem) for elem in codes])

    def __select_code(self):
        self.list_selectcode.delete(0, self.list_selectcode.size() - 1)
        lost_select_code = CombinationsTool.get(
            self.cbb_select_mode_var.get(),
            self.__get_current_opencode(),
            self.__calculate_lost_all(),
            int(self.tf_range_min_var.get()),
            int(self.tf_range_max_var.get()),
            int(self.tf_repeat_cnt_var.get()),
            self.rb_lost_repeat_cnt.get(),
            int(self.cbb_select_odd_var.get().split('-')[0]) if self.ckb_is_allow_odd_var.get() else -1,
            self.tf_range_sum_min_var.get(),
            self.tf_range_sum_max_var.get(),
            [int(num) for num in
             self.tf_contains_codes_var.get().strip().split(' ')] if self.tf_contains_codes_var.get().strip() else [])

        for code in lost_select_code:
            self.list_selectcode.insert(END, self.__codes_to_lottery(code[0]))
        self.__refresh_selection_results_tips()

    def __save_select_code(self):
        selected_out_codes = self.list_selectcode_out.get(0, END)
        self._lottery.save_selected_codes(selected_out_codes)
        self.__refresh_bingo_selectedcodes_tips()
        self.__save_select_conf()

    def __clear_select_code(self):
        self.list_selectcode_out.delete(0, END)
        self.__save_select_code()

    def __select_all_electcodes(self, event):
        self.list_selectcode.select_set(0, END)

    def __select_all_electcodes_out(self, event):
        self.list_selectcode_out.select_set(0, END)

    def __paste_selectedcodes_out(self, event):
        selected_codes = self.root.clipboard_get()
        lotteries = selected_codes.split('\n')
        try:
            for lottery in lotteries:
                lottery = lottery.strip()
                if lottery == '':
                    continue
                self.list_selectcode_out.insert(END, self.__codes_to_lottery([int(elem) for elem in lottery.split()]))
            self.__save_select_code()
        except Exception as e:
            print('ERROR DATA: {data}'.format(data=selected_codes))
            print('ERROR: {err}'.format(err=e))
            tkmsgbox.showerror('不符合粘贴格式', '示例:\n{err}'.format(err='01 02 03 04 05 06\n01 02 03 04 04 06'))

    def __doubleclick_on_selectcods_list(self, event):
        indexs = list(self.list_selectcode.curselection())
        if len(indexs) > 0:
            selected_items = [self.list_selectcode.get(index) for index in indexs]
            for item in selected_items:
                self.list_selectcode_out.insert(END, item)
            if len(indexs) == self.list_selectcode.size():
                self.list_selectcode.delete(0, END)
            else:
                self.__delete_selected_codes(self.list_selectcode, indexs)
        self.__refresh_selection_results_tips()

    def __doubleclick_on_selectcodes_out_list(self, event):
        indexs = list(self.list_selectcode_out.curselection())
        if len(indexs) > 0:
            selected_items = [self.list_selectcode_out.get(index) for index in indexs]
            for item in selected_items:
                self.list_selectcode.insert(END, item)
            if len(indexs) == self.list_selectcode_out.size():
                self.list_selectcode_out.delete(0, END)
            else:
                self.__delete_selected_codes(self.list_selectcode_out, indexs)
        self.__refresh_selection_results_tips()

    def __delete_on_selectcodes_out_list(self, event):
        indexs = list(self.list_selectcode_out.curselection())
        self.__delete_selected_codes(self.list_selectcode_out, indexs)
        self.__refresh_selection_results_tips()

    def __delete_bingo_selected_codes(self, event):
        indexs = self.__get_last_20_repeat_selected_lottery()
        self.__delete_selected_codes(self.list_selectcode_out, indexs)
        self.__save_select_code()
        self.__refresh_selection_results_tips()

    def __delete_selected_codes(self, listbox, indexs):
        if not indexs:
            return
        elif len(indexs) == 1:
            listbox.delete(indexs[0])
        elif len(indexs) == listbox.size():
            listbox.delete(0, END)
        elif len(indexs) == len(range(indexs[0], indexs[-1] + 1)):
            listbox.delete(indexs[0], indexs[-1])
        else:
            all_codes = listbox.get(0, END)
            new_codes = [all_codes[index] for index in range(listbox.size()) if index not in indexs]
            listbox.delete(0, END)
            for codes in new_codes:
                listbox.insert(END, codes)

    def __has_unsaved_selected_codes(self):
        if self.list_selectcode_out.size() > 0:
            saved_selected_codes = set(self._lottery.selectedcodes)
            unsaved_selected_codes = set(self.list_selectcode_out.get(0, END))
            if len(saved_selected_codes | unsaved_selected_codes) != len(saved_selected_codes):
                return True
        return False

    def __on_closing_window(self):
        if self.__has_unsaved_selected_codes() > 0:
            if tkmsgbox.askokcancel('退出', "有未保存的选注结果, 确认要退出？"):
                self.root.destroy()
        else:
            self.root.destroy()

    def __load_select_conf(self):
        if not os.path.exists(self.DB_SELECTED_CONF_FILE):
            return
        with open(self.DB_SELECTED_CONF_FILE, 'r') as fd:
            save_conf = json.load(fd)
        if not save_conf:
            return
        self.cbb_select_mode_var.set(save_conf['cbb_select_mode_var'])
        self.ckb_is_allow_odd_var.set(save_conf['ckb_is_allow_odd_var'])
        self.cbb_select_odd_var.set(save_conf['cbb_select_odd_var'])
        self.tf_range_min_var.set(save_conf['tf_range_min_var'])
        self.tf_range_max_var.set(save_conf['tf_range_max_var'])
        self.tf_repeat_cnt_var.set(save_conf['tf_repeat_cnt_var'])
        self.rb_lost_repeat_cnt.set(save_conf['rb_lost_repeat_cnt'])
        self.tf_range_sum_min_var.set(save_conf['tf_range_sum_min_var'])
        self.tf_range_sum_max_var.set(save_conf['tf_range_sum_max_var'])
        self.tf_contains_codes_var.set(save_conf['tf_contains_codes_var'])

    def __save_select_conf(self):
        save_conf = {'cbb_select_mode_var': self.cbb_select_mode_var.get(),
                     'ckb_is_allow_odd_var': self.ckb_is_allow_odd_var.get(),
                     'cbb_select_odd_var': self.cbb_select_odd_var.get(),
                     'tf_range_min_var': self.tf_range_min_var.get(), 'tf_range_max_var': self.tf_range_max_var.get(),
                     'tf_repeat_cnt_var': self.tf_repeat_cnt_var.get(),
                     'rb_lost_repeat_cnt': self.rb_lost_repeat_cnt.get(),
                     'tf_range_sum_min_var': self.tf_range_sum_min_var.get(),
                     'tf_range_sum_max_var': self.tf_range_sum_max_var.get(),
                     'tf_contains_codes_var': self.tf_contains_codes_var.get()}
        with open(self.DB_SELECTED_CONF_FILE, 'w') as fd:
            json.dump(save_conf, fd, indent=4, separators=(',', ': '))


App.main()
