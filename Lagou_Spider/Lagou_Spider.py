import time
import random
import re
import six
from scrapy import Selector
import pymysql
import requests
from queue import Queue

conn = pymysql.connect(host="127.0.0.1", user='root', password='104758993',
                       database='spider', port=3306, charset="utf8")
cursor = conn.cursor()

headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36",
        "Referer": "https://www.lagou.com/jobs/list_Python?city=%E5%85%A8%E5%9B%BD&cl=false&"
                   "fromSearch=true&labelWords=&suginput="
    }

proxy = {
        "http": "113.91.143.19"
    }


def request_page(position_queue):
    url = "https://www.lagou.com/jobs/positionAjax.json?needAddtionalResult=false"
    data = {
        "first": "true",
        "pn": 1,
        "kd": "爬虫"
    }

    for i in range(1, 31):
        data["pn"] = i
        proxy["http"] = get_proxy()
        time.sleep(random.randint(5, 10))
        response = requests.post(url, data=data, headers=headers, proxies=proxy)
        result = response.json()
        time.sleep(random.randint(5, 10))
        positions = result['content']['positionResult']['result']
        for position in positions:
            positionId = position['positionId']
            position_url = "https://www.lagou.com/jobs/{0}.html".format(positionId)
            position_queue.put(position_url)

def parse_detail(position_queue):
    positions_info = []
    while True:
        if position_queue.empty():
            break
        url = position_queue.get()
        proxy["http"] = get_proxy()
        time.sleep(random.randint(5, 10))
        response = requests.get(url, headers=headers, proxies=proxy)
        time.sleep(random.randint(5, 10))
        selector = Selector(text=response.text)

        apartment = selector.xpath('//div[@class="company"]/text()').extract()[0]           # 招聘部门
        title = selector.xpath('//div[@class="job-name"]/@title').extract()[0]              # 标题
        publish_time = selector.xpath('//p[@class="publish_time"]/text()').extract()[0]     # 发布时间
        publish_time = publish_time.split("发布于拉勾网")[0].strip()
        job_desc = selector.xpath('//dd[@class="job_bt"]/div').extract()[0].replace(
                                "<div>", '').replace("</div>", '').replace(
                                "<p>", '').replace("</p>", '').strip()                        # 职位描述
        job_advantage = selector.xpath('//dd[@class="job-advantage"]/p/text()').extract()[0]  # 职业诱惑
        job_addr_list= selector.xpath('//div[@class="work_addr"]').extract()[0]
        job_addr_list = remove_tags(job_addr_list).split("\n")
        job_addr_list = [job_addr.strip() for job_addr in job_addr_list if job_addr.strip != "查看地图"]
        job_addr = "".join(job_addr_list)

        salary = selector.xpath('//dd[@class="job_request"]/p/span/text()').extract()[0]    # 薪资
        if '-' in salary:
            salary_min = salary.split('-')[0]
            salary_max = salary.split('-')[1]
        elif '以上' in salary:
            salary_min = salary.split('以上')[0]
            salary_max = salary_min
        city = selector.xpath('//dd[@class="job_request"]/p/span[2]/text()').extract()[0].replace("/", '')
        # 经验要求
        work_experience = selector.xpath('//dd[@class="job_request"]/p/span[3]/text()').extract()[0]
        if '-' in work_experience:
            work_experience_min = work_experience.split('-')[0].replace("经验", '')
            if int(work_experience_min) > 1:
                work_experience_min = work_experience_min + 'years'
            else:
                work_experience_min = work_experience_min + 'year'
            work_experience_max = work_experience.split('-')[1].replace("年", '').replace("/", '').strip() + 'years'
        elif '不限' in work_experience:
            work_experience_min = work_experience.replace("经验不限", "no require")
            work_experience_max = work_experience_min
        elif '以下' in work_experience:
            work_experience_max = work_experience.split("年")[0].replace("经验", "").replace("年", "")
            if int(work_experience_max) > 1:
                work_experience_max = work_experience_max + 'years'
                work_experience_min = work_experience_max
            else:
                work_experience_max = work_experience_max + 'year'
                work_experience_min = work_experience_max
        elif '应届' in work_experience:
            work_experience_min = work_experience.replace("经验应届毕业生 /", "graduates")
            work_experience_max = work_experience_min
        # 学历
        education = selector.xpath('//dd[@class="job_request"]/p/span[4]/text()').extract()[0]
        if "本科" in education:
            education = education.split("本")[0].replace("", "undergraduate")
        elif "大专" in education:
            education = education.split("大")[0].replace("", "junior_college_student")
        elif "不限" in education:
            education = education.replace("学历不限 /", "no require")
        # 职业类型
        job_type = selector.xpath('//dd[@class="job_request"]/p/span[5]/text()').extract()[0]
        if "全职" in job_type:
            job_type = job_type.replace("全职", "full time")
        else:
            job_type = job_type.replace("实习", "fieldwork")
        positions_info.append((apartment, title, salary_min, salary_max, city, work_experience_min, work_experience_max, education, job_type, publish_time, job_advantage, job_desc, job_addr))

    for position_info in positions_info:
        try:
            insert_sql = """
                           insert into lagou_job_requests (apartment, title, salary_min, salary_max, city,
                           work_experience_min, work_experience_max, education, job_type, publish_time,
                           job_advantage, job_desc, job_addr)
                           values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                       """
            cursor.execute(insert_sql, (position_info[0], position_info[1],
                                        position_info[2], position_info[3],
                                        position_info[4], position_info[5],
                                        position_info[6], position_info[7],
                                        position_info[8], position_info[9],
                                        position_info[10], position_info[11],
                                        position_info[12]))
            conn.commit()

        except:
            conn.rollback()

def get_proxy():
    select_sql = "select ip,port from proxy_ip order by rand() limit 1"
    cursor.execute(select_sql)
    for ip_info in cursor.fetchall():
        ip = ip_info[0]
        port = ip_info[1]

        judge_result = judge_proxy(ip, port)
        if judge_result:
            return "http://{0}:{1}".format(ip, port)

def judge_proxy(ip, port):
    proxy_ip = "http://{0}:{1}".format(ip, port)
    http_url = "https://www.baidu.com"

    proxy = {
        "http": proxy_ip,
    }
    response = requests.get(url=http_url, proxies=proxy)
    if response.status_code >= 200 and response.status_code < 300:
        print("effective ip")
        return True
    else:
        print("invalid ip and port")
        return get_proxy()


def remove_tags(text, which_ones=(), keep=(), encoding=None):
    assert not (which_ones and keep), 'which_ones and keep can not be given at the same time'

    which_ones = {tag.lower() for tag in which_ones}
    keep = {tag.lower() for tag in keep}

    def will_remove(tag):
        tag = tag.lower()
        if which_ones:
            return tag in which_ones
        else:
            return tag not in keep

    def remove_tag(m):
        tag = m.group(1)
        return u'' if will_remove(tag) else m.group(0)

    regex = '</?([^ >/]+).*?>'
    retags = re.compile(regex, re.DOTALL | re.IGNORECASE)

    return retags.sub(remove_tag, to_unicode(text, encoding))

def to_unicode(text, encoding=None, errors='strict'):
    """Return the unicode representation of a bytes object `text`. If `text`
    is already an unicode object, return it as-is."""
    if isinstance(text, six.text_type):
        return text
    if not isinstance(text, (bytes, six.text_type)):
        raise TypeError('to_unicode must receive a bytes, str or unicode '
                        'object, got %s' % type(text).__name__)
    if encoding is None:
        encoding = 'utf-8'
    return text.decode(encoding, errors)

def main():
    position_queue = Queue(450)

    request_page(position_queue)
    parse_detail(position_queue)

if __name__ == "__main__":
    main()
