# 选课助理说明 #

## 项目说明
本项目修改自：https://github.com/ThunderingII/ucas_tools/tree/master/ucas_course_helper
本着不断改进的原则，作者在仔细阅读并研究了源代码，进行了部分修改，使得不论在校园网环境下还是在非校园网环境下都可以正常运行。
最后在此感谢原作者的辛苦付出!


## 使用方法 ##
修改private.txt后，在控制台执行
- python main.py
1. 非校园网时：
    修改main.py文件：
    def _init_session(self):
        t = LoginUCAS(True).login_sep()
        self.session = t.session
        self.headers = t.headers
        self.login_jwxk()
2. 校园网时：
    修改main.py文件：
    def _init_session(self):
        t = LoginUCAS().login_sep()
        self.session = t.session
        self.headers = t.headers
        self.login_jwxk()
默认为第1种配置


### private文件说明
private.txt中，各行表示意义如下：

1. 第一行为登录选课系统的账号
2. 第二行为密码
3. 第三行为开始选课的时间，格式固定请不要随便更改格式
3. 第四行及以后每一行为一门课以及是否为学位课（0为否1为是）

如下面的为选择编号为091M4044H（且为学位课）和091M5002H（且为非学位课）

```
091M4044H 1
091M5002H 0
```

### 注意 ###
程序假设课程不冲突，每5S尝试选课一次
在使用之前需要确定课程是不冲突的


## 环境说明
- python 3.5.2
- requests 2.11
- 可选环境：
  - Tesseract-OCR
  - PIL

### 环境安装方法
- pip install requests
- pip install Pillow
- 登录网址默认为 http://onestop.ucas.ac.cn/home/index ，如果为 sep.ucas.as.cn 那么需要在安装如下环境：
  - Tesseract-OCR
    - windows下安装：http://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-setup-3.05.00dev.exe
      - 安装时候勾选Registry settings
    - Linux  \  MAC OS X安装见 https://github.com/tesseract-ocr/tesseract/wiki


## 更新说明
- 根据最新系统进行了修改，解决了登录时验证码的问题
