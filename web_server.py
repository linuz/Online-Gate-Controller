#!/usr/bin/python
# Remote Gate Opener
#
# Made by Dennis <dennismald@gmail.com>
# Todo:
#   Implement logging
#   Implement rate limiting
#   Implement logging of times accessed
#   Implement config file usage


# Used for the HTTP Server
import BaseHTTPServer
import SocketServer

# Libraries for interfacing with Raspberry Pi GPIO Ports
import RPi.GPIO as GPIO

import time

HOST = ""
PORT = 80
PARAMETER = "visitor"
GPIO_PIN = 17

# Set up GPIO pins for Raspberry Pi
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_PIN, GPIO.OUT)

# Function to grab the parameter value from the URL 
def get_parameter_value(url):
    if "?" in url:
        query = url.split("?")[1]
        if "=" in query:
            param,value = query.split("=")
            if param == PARAMETER:
                authenticate_value(value)
                return
            else:
                print "[!] Invalid parameter"
                return
        else:
            print "[!] Invalid query string"
            return
    else:
        print "[!] No query string found"
        return

# Function to authenticate the value with a list of valid visitors
def authenticate_value(v):
    visitors = open("visitors.txt")
    for record in visitors:
        record = record.replace("\n", "")
        name,key = record.split(":")
        if v == key:
            print "[*] Opening gate for " + name
            push_button()
            visitors.close()
            return

    print "[!] No matching keys found"
    visitors.close()
    return

# Interface with the Raspberry Pi to perform the actions
def push_button():
    #RaspPi code to push the button
    GPIO.output(GPIO_PIN, True)
    time.sleep(2)
    GPIO.output(GPIO_PIN, False)
    return

# Class for Web Server
class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    # Respond to GET requests
    def do_GET(s):
        s.send_response(200)
        s.send_header("Content-Type", "text/html")
        s.end_headers() 
        s.wfile.write("<center><h1>Welcome!</h1></center>")
        get_parameter_value(s.path)

    # Hide HTTP request log from stdout
    def log_message(self, format, *args):
        return

if __name__ == '__main__':
    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((HOST, PORT), MyHandler)
    print "[*] Starting Web Server on:"
    print "    Host: " + HOST
    print "    Port: " + str(PORT)
    print "----------------------"
    print ""

try:
    httpd.serve_forever()
except (KeyboardInterrupt):
    print " Keyboard Interrupt detected..."
    print "[!] Closing Server..."
    print ""

GPIO.cleanup()
httpd.server_close()
