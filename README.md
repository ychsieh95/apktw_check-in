# APKTW Check-in

A CLI check-in tool for apk.tw forum.

## Usage

```bash
usage: main.py [-h] -u USERNAME -p PASSWORD [--login-count LOGIN_COUNT] [--log-path LOG_PATH]

A CLI check-in tool for apk.tw forum.

optional arguments:
  -h, --help            show this help message and exit
  -u USERNAME, --username USERNAME
                        the username of account
  -p PASSWORD, --password PASSWORD
                        the password of account
  --login-count LOGIN_COUNT
                        the number of attempts to login again when the login fails
  --log-path LOG_PATH   the file path of the log
```

EXAMPLE:

```bash
$ python main.py --username=test_user --password=test_passwd
2021-03-21 20:19:30.626458 - Login (test_user) successful.
2021-03-21 20:19:36.002160 - Try to check-in.
2021-03-21 20:19:41.376949 - {"碎鑽": "2 個", "鑽石": "0 顆", "經驗": "0", "幫助": "0", "技術": "0", "貢獻": "0", "宣傳": "0 次", "金豆": "0 個", "積分": "0(總積分=經驗+ (幫助X0.01) +技術+(貢獻X0.2) )"}
```