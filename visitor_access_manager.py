#!/usr/bin/python

# Todo:
#   - Implement Google Voice API instead of SMTP
#   - Add port number in link logic
#   - Add detecting of visitor file

# Reading of config file
import ConfigParser

import random
import sys
import os
from time import strftime, localtime

# Libraries needed for sending email
import smtplib
import email
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText

# Grab settings from config file
settings = ConfigParser.RawConfigParser()
visitors = ConfigParser.RawConfigParser()
settings.read("settings.cfg")
smtp_server= settings.get("Email", "SMTP_Server")
smtp_port = settings.getint("Email", "SMTP_Port")
smtp_username = settings.get("Email", "SMTP_Username")
smtp_password = settings.get("Email", "SMTP_Password")
email_from_address = settings.get("Email", "Email_From_Address")
email_subject = settings.get("Email", "Email_Subject")
email_body = settings.get("Email", "Email_Body")
visitor_file = settings.get("File", "Visitor_File")
protocol = settings.get("Web Server", "Protocol")
host = settings.get("Web Server", "Hostname")
parameter = settings.get("Web Server", "Parameter")
keyspace = settings.get("Parameter", "Keyspace")
num_of_characters = settings.getint("Parameter", "Number_of_Characters")

# Make directories if they do not exisit
if "/" in visitor_file:
    if not os.path.exists(os.path.dirname(visitor_file)):
        os.makedirs(os.path.dirname(visitor_file))

# Add visitor to file
def addVisitor(name):
    visitors.read(visitor_file)
    if visitors.has_section(name):
        print ""
        print "[!] Visitor already exsist!"
        print ""
        return
    key = generateKey()
    link = protocol+host+"/?"+parameter+"="+key
    visitors.add_section(name)
    visitors.set(name, "Key", key)
    visitors.set(name, "Date Created", strftime("%Y-%m-%d", localtime())) 
    if raw_input("Send an email/text? (y/N) ") == "y":
        email = raw_input("Email Address: ")
        visitors.set(name, "Email", email)
        sendEmail(email, link)
    else:
        visitors.set(name, "Email")
    with open(visitor_file, 'w+') as visitorfile:
        visitors.write(visitorfile) 
    showLink(name)
    return

# Show link for specific visitor
def showLink(name):
    visitors.read(visitor_file)
    if not visitors.has_section(name):
        print ""
        print "[!] Visitor does not exsist!"
        print ""
        return
    key = visitors.get(name, "Key")
    link = protocol+host+"/?"+parameter+"="+key
    print ""
    print "Link for " + name 
    print "---------------------------"
    print link
    print ""

# Delete visitor from file (Revoke their privillages)
def deleteVisitor(name):
    visitors.read(visitor_file)
    if not visitors.has_section(name):
        print ""
        print "[!] Visitor does not exsist!"
        print ""
        return
    option = raw_input("Are you sure you want to delete " + name +"? (y/N) ")
    if option == "y":
        visitors.remove_section(name)
        with open(visitor_file, 'w+') as visitorfile:
            visitors.write(visitorfile) 
    else:
        return

def generateKey():
    key = ''.join(random.choice(keyspace) for _ in xrange(num_of_characters))
    return key

# Construct and send the email
def sendEmail(email, link):
    msg = MIMEMultipart()
    msg['From'] = email_from_address
    msg['to'] = email
    msg['Subject'] = email_subject
    msg.attach(MIMEText(email_body + " " + link))
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(smtp_username, smtp_password)
    server.sendmail(email_from_address, email, msg.as_string())
    server.quit()
    print "Email sent to " + email
    return

# Print the help
def printHelp():
    print ""
    print "\t-a <NAME>\tAdd visitor"
    print "\t-d <NAME>\tDelete visitor"
    print "\t-l <NAME>\tShow visitor's link"
    print ""
    quit()

if len(sys.argv) < 3:
    printHelp()

option = sys.argv[1]
name = ""
for n in sys.argv[2:]:
    name = name + " " + n 
name = name[1:]

if option == "-a":
    addVisitor(name)
elif option == "-d":
    deleteVisitor(name)
elif option == "-l":
    showLink(name)
else:
    print ""
    print "[!] Invalid Argument"
    printHelp()

