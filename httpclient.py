#!/usr/bin/env python
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
import urllib
import urlparse
import os
import json

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def connect(self, host, port):
        outgoing = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        outgoing.connect((host, port))
        return outgoing

    def get_host(self):
        return self.host

    def get_socket(self):
        return self.socket

    def get_code(self, data):
        return None

    def get_headers(self,data):
        return None

    def get_body(self, data):
        return None

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
        return str(buffer)

    def sendDataWithHeaders(self, data, headers, out_socket):
        # Combine and send headers
        header = "".join(headers)
        out_socket.sendall(header)

        # If there is data, send after
        if data:
            out_socket.sendall(data)

    def sendRequest(self, method, url, args=None):
        # Parse the url into its components
        parsed_url = urlparse.urlparse(url)
        data = None
        # Handle no trailing slash
        if len(parsed_url.path) == 0:
            path = "/"
        else:
            path = parsed_url.path

        # These headers are static
        request_line = method + ' ' + path + ' HTTP/1.1\r\n'
        host = "Host: " + parsed_url.hostname + '\r\n'
        accept_charset = "Accept-Charset: utf-8\r\n"
        headers = [request_line, host, accept_charset]

        # Add content that we're willing to accept if GET
        if (method == 'GET'):
            accept = "Accept: */*\r\n"
            headers.append(accept)

        # If post encode the arguments, calculate content length, prefer application/json replies
        elif (method == 'POST'):
            if (args):
                content_type = "Content-Type: application/x-www-form-urlencoded\r\n"
                data = urllib.urlencode(args)
                accept = "Accept: application/json\r\n"
                content_length = "Content-Length: " + str(len(data)) + "\r\n"
                headers += [accept, content_type, content_length]

        # End headers
        end = "\r\n"
        headers.append(end)
        port = parsed_url.port

        # Assume port 80 if no port found
        if not port:
            port = 80

        # Connect
        outgoing = self.connect(parsed_url.hostname, port)
        # Send the encoded data with specified headers to the connected socket
        self.sendDataWithHeaders(data, headers, outgoing)
        # Retrieve any response
        return_data = self.recvall(outgoing);
        # Parse the response into headers and data
        body = return_data.split('\r\n\r\n')[1]
        code = int(return_data.split(' ')[1])
        # Return code and response body
        return code, body

    def GET(self, url, args=None):
        code, body = self.sendRequest('GET', url, args)
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code, body = self.sendRequest('POST', url, args)
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
        print client.command( sys.argv[2], sys.argv[1] )
    else:
        print client.command( sys.argv[1] )
