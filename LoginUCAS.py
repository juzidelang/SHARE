import codecs
import json
import os
import time
from sys import exit
import requests
from MyOCR import image_to_string


class UserNameOrPasswordError(Exception):
    pass


class LoginUCAS(object):
    def __init__(self, use_onestop=False, vercode_save_name='certCode.jpg'):
        self.username, self.password = LoginUCAS._read_username_and_password()
        self.cnt = False
        self.__BEAUTIFULSOUPPARSE = 'html5lib'  # or use 'lxml'
        self.session = requests.session()
        self.vercode_save_name = vercode_save_name
        self.use_onestop = use_onestop
        self._init_login_url()

    def _init_login_url(self):
        if self.use_onestop:
            self._onestop_init()
        else:
            self._sep_init()

    def _onestop_init(self):
        self.url = {
            'base_url': 'https://onestop.ucas.ac.cn/home/index',
            'verification_code': None,
            'login_url': 'https://onestop.ucas.ac.cn/Ajax/Login/0'
        }
        # self.session.get(self.url['base_url'])
        self.headers = {
            'Host': 'onestop.ucas.ac.cn',
            "Connection": "keep-alive",
            "Referer": 'https://onestop.ucas.ac.cn/home/index',
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.106 Safari/537.36",
            }
        self.post_data = {
            "username": self.username,
            "password": self.password,
            "remember": "checked",

        }

    def _sep_init(self):
        self.url = {
            'base_url': 'http://sep.ucas.ac.cn/',
            'verification_code': 'http://sep.ucas.ac.cn/changePic',
            'login_url': "http://sep.ucas.ac.cn/slogin"
        }
        self.headers = {
            "Host": "sep.ucas.ac.cn",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, sdch",
            "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4",
        }
        self.post_data = {
            "userName": self.username,
            "pwd": self.password,
            "sb": "sb",
            "rememberMe": 1,
        }

    @classmethod
    def _read_username_and_password(cls):
        with codecs.open(r'./private.txt', "r", 'utf-8') as f:
            username = password = None
            for i, line in enumerate(f):
                if i == 0:
                    line = bytes(line.encode('utf-8'))
                    if line[:3] == codecs.BOM_UTF8:
                        line = line[3:]
                    username = line.decode('utf-8').strip()
                elif i == 1:
                    password = line.strip()
                else:
                    break
        return username, password

    def _download_verification_code(self):
        r = self.session.get(self.url['verification_code'], stream=True, headers=self.headers)
        with open(self.vercode_save_name, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
                    f.flush()
        return self.vercode_save_name

    def _need_verification_code(self):
        r = self.session.get(self.url['base_url'])
        return r.text.find('验证码') != -1

    def login_sep(self):
        try:
            if not self.cnt:
                print('Login....' + self.url['base_url'])
            if self.use_onestop:
                # 登录 onestop
                html = self.session.post(
                    self.url['login_url'], data=self.post_data, headers=self.headers).text
                # wireshark发现在进行登录后发生了临时重定向，但是重定向的练剑
                res = json.loads(html)
                html2 = self.session.get(res['msg']).text
                # print(html2)
                if html2.find('<h5><i class="icon-ok"></i>选课系统</h5>') == -1:
                    # 如何没有发现html2中有该字段，说明没有登录进去
                    raise UserNameOrPasswordError
                else:
                    '''
                    html = self.session.get(res['msg']).text
                    '''
                    if not self.cnt:
                        self.cnt = True
                    print("登录成功 {}".format(self.cnt))
            else:
                # 登录sep
                try:
                    '''
                    if self._need_verification_code():
                        cert_code = image_to_string(self._download_verification_code())
                        while not cert_code or len(cert_code) < 4:
                            cert_code = image_to_string(self._download_verification_code())
                            self.post_data["certCode"] = cert_code
                    '''
                    html = self.session.post(self.url['login_url'], data=self.post_data, headers=self.headers).text
                    if html.find('密码错误') != -1:
                        raise UserNameOrPasswordError
                    elif html.find('验证码错误') != -1:
                        time.sleep(2)
                        self.cnt += 1
                        return self.login_sep()
                    print("登录成功 {}".format(self.cnt))
                except requests.exceptions.ConnectionError:
                    print('请检查网络连接')
                    exit(1)
        except UserNameOrPasswordError:
            print('用户名或者密码错误，请检查private文件')
            os.system("pause")
            exit(1)
        except requests.exceptions.ConnectionError:
            self.use_onestop = not self.use_onestop
            self._init_login_url()
            print("login time out, change to " + self.url['base_url'])
            self.cnt += 1
            if self.cnt > 20:
                print("也许是教务处挂了")
                exit(1)
            return self.login_sep()
        return self


if __name__ == '__main__':
    LoginUCAS(True).login_sep()
