# ⭐Request_Spider
## 项目列表
1. 项目1：[Request_lagou](https://github.com/Mrrrrr10/Request_Spider/blob/master/Lagou_Spider/Lagou_Spider.py)
2. 项目2：[Request_linkedin](https://github.com/Mrrrrr10/Request_Spider/blob/master/Linkedin_Spider/Linkedin_Spider.py)
3. 项目3：[Request_Youdao](https://github.com/Mrrrrr10/Request_Spider/blob/master/Youdao_spider/Youdao_Spider.py)


## 项目描述：
### 项目1：[Request_lagou](https://github.com/Mrrrrr10/Request_Spider/blob/master/Lagou_Spider/Lagou_Spider.py)
* **需求**：爬取拉勾爬虫工程师职位，并写入mysql
* **技术栈**：requests，Python，mysql,队列操作
* **说明**：前期的爬虫，代码结构比较混乱

### 项目2：[Request_linkedin](https://github.com/Mrrrrr10/Request_Spider/blob/master/Linkedin_Spider/Linkedin_Spider.py)
* **需求**：按照输入的公司名称，爬取该公司Linkedin员工详细信息
* **说明**：这个项目是copy别人的，我只是看到这个博主的爬虫思想很nice，所以搬运过来记录一下，并且做了小修改，改成python3版本，具体思路可以参看[这个blog](https://blog.csdn.net/Bone_ACE/article/details/71055153)

### 项目3：[Request_Youdao](https://github.com/Mrrrrr10/Request_Spider/blob/master/Youdao_spider/Youdao_Spider.py)
* **需求**：输入文本信息，借助有道翻译的api接口返回翻译后的文本
* **说明**：由于有道翻译做了反爬虫机制，有一个sign参数和salt参数需要post过去，但是这两个参数是加密的，所以F12全局搜索sign，发现salt参数是13位的时间戳，sign是sign: n.md5("fanyideskweb" + e + t + "6x(ZHw]mwzX#u0V7@yfwK")，这种sign加密比较好破解，因为是md5加密，python有对应的库可以轻松搞定，下面就放一张js加密sign参数的代码：![sign加密](https://github.com/Mrrrrr10/Request_Spider/blob/master/Youdao_spider/sign.png)
