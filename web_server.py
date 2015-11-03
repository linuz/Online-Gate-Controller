#!/usr/bin/python
# Remote Gate Opener
#
# Made by Dennis <dennismald@gmail.com>
# Todo:
#   Implement logging
#   Implement rate limiting
#   Implement logging of times accessed
#   Implement config file usage

# Reading of config file
import ConfigParser

# Used for the HTTP Server
import BaseHTTPServer
import SocketServer

# Libraries for interfacing with Raspberry Pi GPIO Ports
import RPi.GPIO as GPIO
import time

# Grab settings from config file
settings = ConfigParser.RawConfigParser()
settings.read("settings.cfg")
hostname = settings.get("Web Server", "Hostname")
port = settings.getint("Web Server", "Port")
parameter = settings.get("Web Server", "Parameter")
response_html = settings.get("Web Server", "Response_HTML")
visitor_file = settings.get("File", "Visitor_File_Name")

# Set up GPIO pins for Raspberry Pi
gpio_pin = settings.getint("Raspberry Pi", "GPIO_Pin")
GPIO.setmode(GPIO.BCM)
GPIO.setup(gpio_pin, GPIO.OUT)

# Function to grab the parameter value from the URL 
def get_parameter_value(url):
    if "?" + parameter + "=" in url:
        authenticate_value(url.split("?" + parameter + "=")[1])
    else:
        return

# Function to authenticate the value with a list of valid visitors
def authenticate_value(v):
    visitors = open(visitor_file)
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
    GPIO.output(gpio_pin, True)
    time.sleep(2)
    GPIO.output(gpio_pin, False)
    return

# Class for Web Server
class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    # Respond to GET requests
    def do_GET(s):
        s.send_response(200)
        s.send_header("Content-Type", "text/html")
        s.end_headers() 
        s.wfile.write(response_html)
        get_parameter_value(s.path)

    # Hide HTTP request log from stdout
    def log_message(self, format, *args):
        return

if __name__ == '__main__':
    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((hostname, port), MyHandler)
    print "[*] Starting Web Server on:"
    print "    Host: " + hostname
    print "    Port: " + str(port)
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
