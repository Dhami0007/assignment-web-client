#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        
        return None

    def get_code(self, data):
        data = data.split('\r\n')
        return data[0].split()[1]

    def get_headers(self,data):

        return data[0]

    def get_body(self, data):
        
        return data[1]
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        #self.socket.sendall(data.encode('latin-1'))

    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part

        return buffer.decode('utf-8')
        #return buffer.decode('latin-1')
    
    def GET(self, url, args=None):

        # parsing done using the urllib parsing: https://docs.python.org/3/library/urllib.parse.html
        parsed_url = urllib.parse.urlparse(url)
        path = parsed_url.path
        if path == '':
            path= '/'
        host = parsed_url.hostname
    
        port = parsed_url.port

        if port == None:
            port=80
        
        # with TA consultation
        req = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nAccept: */*\r\nConnection: close\r\n\r\n"

        self.connect(host, port)
        self.sendall(req)
        #self.socket.shutdown(socket.SHUT_WR)
        result = self.recvall(self.socket)
        self.close()

        parsed_result = result.split('\r\n\r\n')
        header = self.get_headers(parsed_result)
        print(f"Header:\n{header}")

        code = int(self.get_code(header))
        print(f"Code:\n{code}")

        body = self.get_body(parsed_result)
        print(f"Body:\n{body}")
        
        return HTTPResponse(code, body)

    def POST(self, url, args=None):

        # parsing done using the urllib parsing: https://docs.python.org/3/library/urllib.parse.html
        parsed_url = urllib.parse.urlparse(url)
        path = parsed_url.path
        if path == '':
            path= '/'
        host = parsed_url.hostname
        port = parsed_url.port
        if port == None:
            port = 80
        
        # we will be getting the content to post from args arguement of the function

        if args == None:
            args = ""
        else:
            args = urllib.parse.urlencode(args)

        content_length = len(args)

        # with TA consultation and 
        # https://sentry.io/answers/how-are-parameters-sent-in-an-http-post-request/#:~:text=A%20POST%20request%20is%20often,of%20the%20element.
        req = f"POST {path} HTTP/1.1\r\nHost: {host}\r\nAccept: */*\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: {content_length}\r\n\r\n{args}\r\nConnection: close\r\n\r\n"
        
        self.connect(host, port)
        self.sendall(req)
        # self.socket.shutdown(socket.SHUT_WR)
        result = self.recvall(self.socket)
        self.close()

        print(f"This is what we are receiving:\n{result}")

        parsed_result = result.split('\r\n\r\n')
        print(parsed_result)
        header = self.get_headers(parsed_result)
        print(f"Header:\n{header}")

        code = int(self.get_code(header))
        print(f"Code:\n{code}")

        body = self.get_body(parsed_result)
        print(f"Body:\n{header}")

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))