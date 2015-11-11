#!/usr/bin/python
# Remote Gate Opener
#
# Made by Dennis <dennismald@gmail.com>
# Todo:
#   Implement rate limiting
#   Remove Server headers
#   Secure webserver
#   GPIO requires root. Fix this to not require root

# Reading of config file
import ConfigParser

# Used for the HTTP Server
import cherrypy
import os

# Libraries for interfacing with Raspberry Pi GPIO Ports
import RPi.GPIO as GPIO
import time
from time import strftime, localtime

# Grab settings from config file
settings = ConfigParser.RawConfigParser()
visitors = ConfigParser.RawConfigParser()
settings.read("settings.cfg")
#host = settings.get("Web Server", "Hostname")
host = "0.0.0.0"
port = settings.getint("Web Server", "Port")
parameter = settings.get("Web Server", "Parameter")
response_html = settings.get("Web Server", "Response_HTML")
visitor_file = settings.get("File", "Visitor_File")

# Log files
web_server_access_log_file = settings.get("Logs", "Web_Server_Access_Log")
web_server_error_log_file = settings.get("Logs", "Web_Server_Error_Log")
visitor_log_file = settings.get("Logs", "Visitor_Log")

# Check for exisitance of visitor file
if not os.path.exists(visitor_file):
    print "[!] " + visitor_file + " not found!"
    quit()

# Make directories if they do not exisit
if "/" in web_server_access_log_file:
    if not os.path.exists(os.path.dirname(web_server_access_log_file)):
        os.makedirs(os.path.dirname(web_server_access_log_file))
if "/" in web_server_error_log_file:
    if not os.path.exists(os.path.dirname(web_server_error_log_file)):
        os.makedirs(os.path.dirname(web_server_error_log_file))
if "/" in visitor_log_file:
    if not os.path.exists(os.path.dirname(visitor_log_file)):
        os.makedirs(os.path.dirname(visitor_log_file))

#Web Server config
cherrypy.config.update({'server.socket_host': host,
                        'server.socket_port': port,
                        'environment': 'production',
                        'log.access_file': web_server_access_log_file,
                        'log.error_file': web_server_error_log_file
                        })

# Set up GPIO pins for Raspberry Pi
gpio_pin = settings.getint("Raspberry Pi", "GPIO_Pin")
GPIO.setmode(GPIO.BCM)
GPIO.setup(gpio_pin, GPIO.OUT)

# Function to authenticate the value with a list of valid visitors
def authenticate_value(v):
    visitors.read(visitor_file)
    for name in visitors.sections():
        if visitors.get(name, "Key") == v:
            print "[*] " + strftime("%Y-%m-%d %H:%M:%S", localtime()) + " - Access Granted for " + name
            with open(visitor_log_file, "a") as visitor_log:
                visitor_log.write(strftime("%Y-%m-%d %H:%M:%S", localtime()) + " - Access Granted for " + name + "\n")
            push_button()
            return
    print "[!] " + strftime("%Y-%m-%d %H:%M:%S", localtime()) + " - No matching keys found"
    with open(visitor_log_file, "a") as visitor_log:
        visitor_log.write(strftime("%Y-%m-%d %H:%M:%S", localtime()) + " - No matching keys found" + "\n")
    return

# Interface with the Raspberry Pi to perform the actions
def push_button():
    GPIO.output(gpio_pin, True)
    time.sleep(2)
    GPIO.output(gpio_pin, False)
    return

#CherryPy web server class
class WebServer(object):
    @cherrypy.expose
    def index(self, **params):
        if parameter in params:
            authenticate_value(params[parameter])
            return response_html
        return response_html

if __name__ == '__main__':
    print ""
    print "Starting Web Server on 0.0.0.0:" + str(port)
    print ""
    cherrypy.quickstart(WebServer())
    GPIO.cleanup()
