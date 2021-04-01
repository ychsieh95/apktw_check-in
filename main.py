import argparse
import copy
import json
import os
import requests
import time
from datetime import datetime
from lxml import etree


def logger(log_str, log_path=''):
    datetime_now = datetime.now()
    print(f'{datetime_now} - {log_str}')

    if log_path:
        with open(log_path, 'a+', encoding='utf8') as f:
            f.write(f'{datetime_now} - {log_str}\n')


class ApkTw:
    def __init__(self, username, password):
        self.username = username
        self.password = password

        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36 Edg/88.0.705.74'}

    def login(self):
        url = 'https://apk.tw/member.php?mod=logging&action=login&loginsubmit=yes&infloat=yes&lssubmit=yes&inajax=1'
        data = {
            'username': self.username,
            'password': self.password,
            'quickforward': 'yes',
            'handlekey': 'ls'}
        resp_content = self.session.post(url, data=data, headers=self.headers).content.decode('utf8')

        if '歡迎您回來' in resp_content:
            return True, ''
        else:
            out_flag = False
            out_message = ''
            for fragment in resp_content.split('\''):
                if out_flag:
                    out_message = fragment
                    break
                elif 'errorhandle_(' in fragment or 'errorhandle_ls('  in fragment:
                    out_flag = True
            return False, out_message

    def check_state(self):
        # if un-check-in:
        #     <a id="my_amupper" href="javascript:;" onclick="ajaxget('plugin.php?id=dsu_amupper:pper&ajax=1&formhash=c272a519&zjtesttimes=1488651652', 'my_amupper', 'my_amupper', '簽到中', '',function () {toneplayer(0);});">
        #         <img src="./source/plugin/dsu_amupper/images/dk.gif" style="margin-bottom:-6px;">
        #     </a>
        # if check-in:
        #     <a id="ppered" onmouseover="delayShow(this)" href="plugin.php?id=dsu_amupper:list" target="_blank" initialized="true">
        #         <img src="./source/plugin/dsu_amupper/images/wb.gif" style="margin-bottom:-6px;">
        #     </a>
        url = 'https://apk.tw/forum-soft-1.html'
        resp_content = self.session.get(url, headers=self.headers).content.decode('utf8')
        html = etree.HTML(resp_content)
        return True if html.xpath('//a[@id="my_amupper"]') else False

    def check_in(self):
        url = 'https://apk.tw/forum-soft-1.html'
        resp_content = self.session.get(url, headers=self.headers).content.decode('utf8')
        time.sleep(2)

        html = etree.HTML(resp_content)
        onclick = html.xpath('//a[@id="my_amupper"]')[0].attrib['onclick']
        href = onclick.split('\'')[1]
        url = 'https://apk.tw/' + href
        headers = copy.deepcopy(self.headers)
        headers.update({
            'Accept': '*/*',
            'Accept-Encoding': '',
            'X-Requested-With': 'XMLHttpRequest'})
        response = self.session.get(url, headers=headers)

    def get_info(self):
        url = 'https://apk.tw/home.php?mod=spacecp&ac=credit'
        resp_content = self.session.get(url, headers=self.headers).content.decode('utf8')
        html = etree.HTML(resp_content)

        data = {}
        for elem in html.xpath('//*[@id="ct"]/div[1]/div/ul[2]/li'):
            keyvalue = ''.join([t.strip() for t in elem.itertext()]).split(':')
            data[keyvalue[0].strip()] = keyvalue[1].strip().replace('立即充值»', '')
        return json.dumps(data, ensure_ascii=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A CLI check-in tool for apk.tw forum.')
    parser.add_argument('-u', '--username', required=True, help='the username of account')
    parser.add_argument('-p', '--password', required=True, help='the password of account')
    parser.add_argument('--login-count', type=int, default=5, help='the number of attempting to login again when the login fails')
    parser.add_argument('--login-interval', type=int, default=30, help='the interval of attempting to login again when the login fails (seconds)')
    parser.add_argument('--log-path', default='./apktw_check-in.log', help='the file path of the log')
    args = parser.parse_args()
    print(args)

    apktw = ApkTw(username=args.username, password=args.password)
    login_count = 1
    try:
        while login_count <= args.login_count:
            login_state, login_message = apktw.login()
            if not login_state:
                login_count += 1
                logger(f'Login ({args.username}) failed. ({login_message})')
                logger(f'Re-login after ({args.login_interval}) second(s).')
                time.sleep(args.login_interval)
                continue
            else:
                logger(f'Login ({args.username}) successful.', args.log_path)
                time.sleep(5)
                if not apktw.check_state():
                    logger('Already check-in today.', args.log_path)
                    time.sleep(5)
                else:
                    try:
                        logger('Try to check-in.', args.log_path)
                        apktw.check_in()
                        time.sleep(5)
                    except Exception as error:
                        # [<class 'requests.exceptions.ContentDecodingError'>]
                        #     ('Received response with content-encoding: gzip, but failed to decode it.', error('Error -3 while decompressing data: incorrect header check'))
                        logger(f'[{type(error)}] {error}', args.log_path)
                logger(apktw.get_info())
                break
    except Exception as error:
        login_count += 1
        logger(f'[{type(error)}] {error}', args.log_path)