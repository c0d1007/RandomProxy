#encoding=utf8
"""
author thing2no@163.com
Linux:Python2 32/64bit
Windows:Python2 32bit (pycurl=>libcurl only suporrt python 32bit now)
"""
import os
import sys
import json
import time
import random
import socket
import requests
import tornado.web
import tornado.ioloop
import tornado.iostream
import tornado.httpclient
import tornado.httpserver
from optparse import OptionParser
from tornado.httpclient import HTTPRequest
try:
    from tornado.curl_httpclient import CurlAsyncHTTPClient as AsyncHTTPClient
except ImportError:
    from tornado.simple_httpclient import SimpleAsyncHTTPClient as AsyncHTTPClient
qu = []
qu_index = 0
args = None
options = None
host_ip = "127.0.0.1"
host_port = 8888
time_wait = 0  #options.change
change_flag = True
start_time = time.time()
IPProxyPool = "http://127.0.0.1:8000/?protocol=2"

def cmd_help():
    global args
    global options
    global time_wait
    global host_ip
    global host_port
    global IPProxyPool
    usage = "python %s [-H 127.0.0.1] [-p 8888] [-c 0] [-a http://127.0.0.1:8000] [-t 0] [-p 2]" % __file__
    opt = OptionParser(usage)
    opt.add_option('-H','--host',
                    dest='host_ip',
                    type=str,
                    default="127.0.0.1",
                    help='[RandomProxy] The RandomProxy listen host_ip; default 127.0.0.1')
    opt.add_option('-p','--port',
                    dest="host_port",
                    type=int,
                    default=8888,
                    help="[RandomProxy] The RandomProxy listen host_port; default 8888")
    opt.add_option('-c','--change',
                    dest="change",
                    type=int,
                    default=0,
                    help="[RandomProxy] Default (0); (0): every request has a new IP; (60): Change IP every 60 seconds  ;  (less than 0): request 127.0.0.1:8888/next to change IP")
    opt.add_option('-a','--address',
                    dest="address",
                    type=str,
                    default="http://127.0.0.1:8000",
                    help="[IPProxyPool] The IPProxyPool api url;default http://127.0.0.1:8000")
    opt.add_option('-t','--type',
                    dest="type",
                    type=int,
                    default=0,
                    help="[IPProxyPool] Default (0): high anonymous, (1): anonymous, (2) transparent")
    opt.add_option('-P','--protocol',
                    dest="protocol",
                    type=int,
                    default=2,
                    help="[IPProxyPool] HTTP/HTTPS proxy you want ? (0): http, (1) https, (2) http/https(default)")
    (options, args) = opt.parse_args()
    time_wait = options.change
    host_ip = options.host_ip
    host_port = options.host_port
    #print(time_wait,change_flag)
    IPProxyPool = options.address + "/?protocol=%s&type=%s" % (options.protocol,options.type)
    #opt.print_help()

def get_qu(url=IPProxyPool):
    global qu
    global qu_index
    r = requests.get(IPProxyPool)
    qu = json.loads(r.text)
    qu_index = 0   

def get_proxy(url=IPProxyPool):
    global qu
    global qu_index
    global start_time
    global change_flag
    print(time_wait,change_flag)
    if time_wait < 0 :
        if change_flag == True:
            for i in range(3):
                if qu_index == len(qu):
                    get_qu(IPProxyPool)
                else:
                    qu_index += 1
                    start_time = time.time()
                    change_flag = False
                    return qu[qu_index]
        else:
            return qu[qu_index]
    else:   
        if time_wait > time.time() - start_time:
            return qu[qu_index]     
        else:
            start_time = time.time()
            for i in range(3):
                if qu_index == len(qu):
                    get_qu(IPProxyPool)
                else:
                    qu_index += 1
                    return qu[qu_index]
    sys._exit()


class DetailHandler(tornado.web.RequestHandler):
    SUPPORTED_METHODS = ['GET', 'POST', 'CONNECT']
    @tornado.web.asynchronous
    def get(self):
        global change_flag
        global start_get_proxy
        print ("Get->", self.request.uri)
        print (str(self.request))
        protocol = self.request.protocol
        host = self.request.host
        method = self.request.method
        uri = self.request.uri
        headers = self.request.headers
        if host in "%s:%d"%(host_ip,host_port) and "next" in uri:
            change_flag = True
        proxy = get_proxy()
        AsyncHTTPClient().fetch(
            HTTPRequest(
                        url = uri,
                        method = method,
                        headers = headers,
                        validate_cert=False,
                        proxy_host=proxy[0],
                        proxy_port=proxy[1]
                ),
            self.on_response)

    def on_response(self, respnose):
        print (respnose)
        self.write (respnose.body)
        self.finish()

    @tornado.web.asynchronous
    def post(self):
        print( "Post->", self.request.uri)
        print (str(self.request))
        method = self.request.method
        uri = self.request.uri
        headers = self.request.headers
        body = self.request.body
        proxy = get_proxy()
        AsyncHTTPClient().fetch(
            HTTPRequest(
                url=uri,
                method=method,
                headers=headers,
                body=body,
                validate_cert=False,
                proxy_host=proxy[0],
                proxy_port=proxy[1]
            ),
            self.on_response)

    @tornado.web.asynchronous
    def connect(self):
        global start_get_proxy
        print('Start CONNECT to %s', self.request.uri)
        print( "Connect->",self.request.uri)
        host, port = self.request.uri.split(':')
        client = self.request.connection.stream
        def read_from_client(data):
            upstream.write(data)
            
        def read_from_upstream(data):
            client.write(data)
            
        def client_close(data=None):
            if upstream.closed():
                return
            if data:
                upstream.write(data)
            upstream.close()
             
        def upstream_close(data=None):
            if client.closed():
                return
            if data:
                client.write(data)
            client.close()
            
        def start_tunnel():
            print('CONNECT tunnel established to %s', self.request.uri)
            client.read_until_close(client_close, read_from_client)
            upstream.read_until_close(upstream_close, read_from_upstream)
            client.write(b'HTTP/1.0 200 Connection established\r\n\r\n')
            
        def on_proxy_response(data=None):
            if data:
                first_line = data.splitlines()[0]
                http_v, status, text = first_line.split(None, 2)
                if int(status) == 200:
                    print('Connected to upstream proxy %s', proxy)
                    start_tunnel()
                    return
            self.set_status(500)
            self.finish()
            
        def start_proxy_tunnel():
            upstream.write('CONNECT %s HTTP/1.1\r\n' % self.request.uri)
            upstream.write('Host: %s\r\n' % self.request.uri)
            upstream.write('Proxy-Connection: Keep-Alive\r\n\r\n')
            upstream.read_until('\r\n\r\n', on_proxy_response)          
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        upstream = tornado.iostream.IOStream(s)
        proxy = get_proxy()
        if proxy:
            proxy_host, proxy_port = proxy[0],proxy[1]
            upstream.connect((proxy_host, proxy_port), start_proxy_tunnel)
        else:
            upstream.connect((host, port), start_tunnel)

def make_app():
    return tornado.web.Application([
        (r".*",DetailHandler),
    ])

def main():
    app =make_app()
    app.listen(host_port, address=host_ip)
    print("RandomProxy runing on %s:%d "%(host_ip,host_port))
    tornado.ioloop.IOLoop.current().start()

if __name__ == '__main__':
    cmd_help()
    if "nt" in os.name:
        os.system("start python IPProxyPool/IPProxy.py")
    else:
        os.system("python IPProxyPool/IPProxy.py  & ")
    while len(qu) < 10:
        print (" IP less than 10 ")
        try:
            r = requests.get(IPProxyPool)
            qu = json.loads(r.text)
            print (IPProxyPool,qu_index,qu)
        except:
            print( " Wait for ProxyPool " + IPProxyPool)
        time.sleep(1)   
    qu_index = 0
    main()