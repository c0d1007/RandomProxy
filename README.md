# RandomProxy


##From the Internet to capture a large number of proxy IP, and then through the agent cascade to achieve random forwarding traffic. Compatible with most support HTTP / HTTPS proxy procedures, such as Sqlmap, Burpsuite, FireFox, you can also run on Linux, Windows, MacOS.##
```
Usage: python random_proxy.py [-H 127.0.0.1] [-p 8888] [-c 0] [-a http://127.0.0.1:8000] [-t 0] [-p 2]

Options:
  -h, --help            show this help message and exit
  -H HOST_IP, --host=HOST_IP
                        [RandomProxy] The RandomProxy listen host_ip; default
                        127.0.0.1
  -p HOST_PORT, --port=HOST_PORT
                        [RandomProxy] The RandomProxy listen host_port;
                        default 8888
  -c CHANGE, --change=CHANGE
                        [RandomProxy] Default (0); (0): every request has a
                        new IP; (60): Change IP every 60 seconds  ;  (less
                        than 0): request 127.0.0.1:8888/next to cahnge IP
  -a ADDRESS, --address=ADDRESS
                        [IPProxyPool] The IPProxyPool api url;default
                        http://127.0.0.1:8000
  -t TYPE, --type=TYPE  [IPProxyPool] Default (0): high anonymous, (1):
                        anonymous, (2) transparent
  -P PROTOCOL, --protocol=PROTOCOL
                        [IPProxyPool] HTTP/HTTPS proxy you want ? (0): http,
                        (1) https, (2) http/https(default)
```
Install 
```
1. random_proxy
pip install request tornado pycurl
2. IPProxyPool
Refer https://github.com/qiyeboy/IPProxyPool
```

Reference
```
qiyeboy/IPProxyPool: IPProxyPool代理池项目，提供代理ip
https://github.com/qiyeboy/IPProxyPool
rfyiamcool/toproxy: 😈 high performance simple tornado http proxy.
https://github.com/rfyiamcool/toproxy
```
PS
```
if something worry on windows,
because that pycurl not support python 64bit on windows.
you can install python3 32 bit to solove it.

```
