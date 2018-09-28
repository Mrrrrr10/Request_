import time
import json
import hashlib
import requests
from fake_useragent import UserAgent

url = "http://fanyi.youdao.com/translate?smartresult=dict&smartresult=rule"
headers = {
    "User-Agent": UserAgent().random
}

def main():
    def get_salt():
        """获取13位时间戳"""
        salt = str(int(round(time.time() * 1000)))
        return salt

    def get_sign():
        """获取sign"""
        sign = "fanyideskweb" + keywords + get_salt() + "6x(ZHw]mwzX#u0V7@yfwK"
        hl = hashlib.md5()
        hl.update(sign.encode(encoding='utf-8'))
        return sign

    data = {
        'i': keywords,
        'from': 'AUTO',
        'to': 'AUTO',
        'smartresult': 'dict',
        'client': 'fanyideskweb',
        'salt': get_salt(),
        'sign': get_sign(),
        'doctype': 'json',
        'version': '2.1',
        'keyfrom': 'fanyi.web',
        'action': 'FY_BY_REALTIME',
        'typoResult': 'false'
    }

    response = requests.post(url, data=data, headers=headers)
    try:
        try:
            if response.status_code == 200:
                text_json = json.loads(response.text)
                word = text_json.get('translateResult')[0][0].get('tgt')
                print("翻译结果：", word)
        except requests.exceptions.ConnectionError:
            print("请求出错")
    except Exception as e:
        print(e)


if __name__ == '__main__':
    print('【INFO】：输入需要翻译的文本, 输入exit退出翻译')
    while True:
        keywords = input("请输入翻译文本：")
        if keywords == "exit":
            break
        main()

