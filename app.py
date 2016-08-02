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
            # for num in item['opencode'].split(','):
            #     if '+' in num:
            #         lottery['code'].extend(num.split('+'))
            #         bluecode = int(num.split('+')[1])
            #     else:
            #         lottery['code'].append(num)
            # lottery['redcode'] = [int(num) for num in lottery['code'] if int(num) != bluecode]
            # lottery['bluecode'] = bluecode
            lottery['lostcode'] = list(set(self.DEFAULT_CODE) - set(lottery['redcode']))
            lotteries[lottery['expect']] = lottery
        self._data.update(lotteries)

    def __load(self):
        try:
            if os.path.exists(self.DB_FILE):
                with open(self.DB_FILE, 'r') as fd:
                    self._data = json.load(fd)
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
        self.style.theme_use(random_theme)
        self.root.title('遗漏选号')
        self.root.geometry('600x480+0+0')
        self._lottery = LotteryQurey()
        self.__initialize_components()

    def __initialize_components(self):
        # self._lottery.refresh()
        self.lbSelection = tk.Label(self.root, text="查看：")
        self.lbSelection.pack()

        lottery_edition = StringVar()
        self.cbbSelection = ttk.Combobox(self.root, textvariable=lottery_edition)
        self.cbbSelection['value'] = self._lottery.edition
        self.cbbSelection['state'] = 'readonly'
        self.cbbSelection.bind('<<ComboboxSelection>>', self.edition_change)
        self.cbbSelection.current(1)
        self.cbbSelection.pack()

        self.btnSelection = tk.Button(self.root, text="刷新", command=self.refresh)
        self.btnSelection.pack()

    def edition_change(self):
        print('edition changed!')

    def refresh(self):
        print('refresh from internet')


app = App()
app.root.mainloop()
