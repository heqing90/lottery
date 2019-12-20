import requests as req
import json
import csv

def dump_results(results):
    with open('results.csv', 'w', newline='') as csvfile:
        fieldnames = ['编码', '日期', '红球', '红球1', '红球2', '红球3', '红球4', '红球5', '红球6', '蓝球', '销售额', '奖金池', "中奖信息", "提示"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in results:
            red = [int(x.strip()) for x in row['red'].split(',')]
            writer.writerow(
                {
                   '编码': row['code'], 
                   '日期': row['date'], 
                   '红球': row['red'], 
                   '红球1': red[0], 
                   '红球2': red[1], 
                   '红球3': red[2], 
                   '红球4': red[3], 
                   '红球5': red[4], 
                   '红球6': red[5], 
                   '蓝球': row['blue'], 
                   '销售额': row['sales'],
                   '奖金池': row['poolmoney'], 
                   "中奖信息": row['content'], 
                   "提示": row['msg']
                }
            )


def print_json(obj):
    print(json.dumps(obj, indent=4, separators=(",", ":")))

url = """http://www.cwl.gov.cn/cwl_admin/kjxx/findDrawNotice?name=ssq&issueCount=&issueStart=&issueEnd=&dayStart=2013-01-01&dayEnd=2019-12-20&pageNo="""
headers = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Connection": "keep-alive",
    "Cookie": "UniqueID=0zTYYQZui07HNSBz1576828876029; Sites=_21; _ga=GA1.3.133741631.1576828928; _gid=GA1.3.452061671.1576828928; 21_vq=2; _Jo0OQK=636F4623EEF353308AAC44FA21F9F33C6D00E2A7F7D3F28837193E3DFFE657B5BCD5F14899E487D1BCACCEAD2AB862703A8499B4C2F82C974EAAB5E61EA0319BA75F1B3C19C5B2FC5F8E6E66EDA7420CD4BE6E66EDA7420CD4B5B675FB7B14551AD3328EEBACF9E4A3CGJ1Z1Vw==",
    "Host": "www.cwl.gov.cn",
    "Referer": "http://www.cwl.gov.cn/kjxx/ssq/kjgg/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
}
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
        more_url =  url + page 
        print(more_url)
        r = req.get(more_url, headers=headers)
        if r.status_code == 200:
            more_data = json.loads(r.text)
            results.extend(more_data['result']) 

print("Got results=", len(results))
#for e in results:
 #   print('code=', e['code'], "date=", e['date'], 'red=', e['red'], 'blue=', e['blue'])

dump_results(results)
