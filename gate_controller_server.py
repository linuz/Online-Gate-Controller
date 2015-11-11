#!/usr/bin/python
# Remote Gate Opener
#
# Made by Dennis <dennismald@gmail.com>
# Todo:
#   Implement rate limiting

# Reading of config file
import ConfigParser

# Used for the HTTP Server
import BaseHTTPServer
import SocketServer
import os

# Libraries for interfacing with Raspberry Pi GPIO Ports
import RPi.GPIO as GPIO
import time
from time import strftime, gmtime

# Grab settings from config file
settings = ConfigParser.RawConfigParser()
visitors = ConfigParser.RawConfigParser()
settings.read("settings.cfg")
hostname = settings.get("Web Server", "Hostname")
port = settings.getint("Web Server", "Port")
parameter = settings.get("Web Server", "Parameter")
response_html = settings.get("Web Server", "Response_HTML")
visitor_file = settings.get("File", "Visitor_File")

# Log files
web_server_access_log_file = settings.get("Logs", "Web_Server_Access_Log")
visitor_log_file = settings.get("Logs", "Visitor_Log")

# Check for exisitance of visitor file
if not os.path.exists(visitor_file):
    print "[!] " + visitor_file + " not found!"
    quit()

# Make directories if they do not exisit
if "/" in web_server_access_log_file:
    if not os.path.exists(os.path.dirname(web_server_access_log_file)):
        os.makedirs(os.path.dirname(web_server_access_log_file))
if "/" in visitor_log_file:
    if not os.path.exists(os.path.dirname(visitor_log_file)):
        os.makedirs(os.path.dirname(visitor_log_file))

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
    visitors.read(visitor_file)
    for name in visitors.sections():
        if visitors.get(name, "Key") == v:
            print "[*] " + str(strftime("%Y-%m-%d %H:%M:%S", gmtime())) + " - Access Granted for " + name
            with open(visitor_log_file, "a") as visitor_log:
                visitor_log.write(str(strftime("%Y-%m-%d %H:%M:%S", gmtime())) + " - Access Granted for " + name + "\n")
            push_button()
            return
    print "[!] " + str(strftime("%Y-%m-%d %H:%M:%S", gmtime())) + " - No matching keys found"
    with open(visitor_log_file, "a") as visitor_log:
        visitor_log.write(str(strftime("%Y-%m-%d %H:%M:%S", gmtime())) + " - No matching keys found" + "\n")
    return

# Interface with the Raspberry Pi to perform the actions
def push_button():
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
        with open(web_server_access_log_file, "a") as web_server_access_log:
            web_server_access_log.write("%s - - [%s] %s\n" % (self.address_string(), self.log_date_time_string(), format%args))
        return

if __name__ == '__main__':
    
    #
    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((hostname, port), MyHandler)
    print ""
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
