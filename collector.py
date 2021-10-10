import requests as req
import json
import time


def print_json(obj):
    print(json.dumps(obj, indent=4, separators=(",", ":")))


base_query_url = """http://www.cwl.gov.cn/cwl_admin/front/cwlkj/search/kjxx/findDrawNotice?name=ssq&issueCount=&issueStart=&issueEnd=&dayStart={}&dayEnd={}"""
headers = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Connection": "keep-alive",
    "Cookie": "HMF_CI=f59a5e9c98b5baa2b595275463fc77617c2c6d4297cb33199777194a694b61c677; 21_vq=7",
    "Host": "www.cwl.gov.cn",
    "Referer": "http://www.cwl.gov.cn/kjxx/ssq/kjgg/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
}

def today():
    return time.strftime("%Y-%m-%d", time.localtime()) 

def get_all_lottery_codes_by_date(start_date, end_date):
    if start_date is None:
        start_date = "2013-01-01"
    if end_date is None:
        end_date = today()
    if start_date == end_date:
        return []
    url = base_query_url.format(start_date, end_date)
    r = req.get(url, headers=headers)
    if r.status_code != 200:
        print("Failed to get...")
        assert(False)
    data = json.loads(r.text)
    # print_json(data)
    pages = data['pageCount']
    results = data['result']
    if pages > 1:
        for page in [str(x) for x in range(1, pages + 1)]:
            more_url =  url + '&pageNo=' + page 
            print(more_url)
            r = req.get(more_url, headers=headers)
            if r.status_code == 200:
                more_data = json.loads(r.text)
                results.extend(more_data['result']) 
    return results

