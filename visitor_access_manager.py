#!/usr/bin/python

# Reading of config file
import ConfigParser

import string
import random
import sys
import os.path

import smtplib
import email
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText

# Grab settings from config file
settings = ConfigParser.RawConfigParser()
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
hostname = settings.get("Web Server", "Hostname")
parameter = settings.get("Web Server", "Protocol")
keyspace = settings.get("Parameter", "Keyspace")
num_of_characters = settings.getint("Parameter", "Number_of_Characters")

def sendEmail(email, link):
    msg = MIMEMultipart()
    msg['From'] = email_from_address
    msg['to'] = email
    msg['Subject'] = email_subject
    msg.attach(MIMEText(email_body + link))
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(smtp_username, smtp_password)
    server.sendmail(email_from_address, email, msg.as_string())
    server.quit()

def constructAuth():
    auth=''.join(random.choice(keyspace) for _ in xrange(num_of_characters))
    return auth

def checkAuthFile():
    if not os.path.exists(visitor_file):
        file(visitor_file, 'w').close()

def addUser(name):
    checkAuthFile()
    with open(visitor_file, 'a') as f:
        auth=constructAuth()
        f.write(name + ':' + auth + '\n')
        print(name + ' Added to the file with auth key ' + auth)
        return auth

def readFileContents():
    checkAuthFile()
    with open(visitor_file, 'r') as f:
        fileContents=f.readlines()
        return fileContents

def searchForUser(name, userList):
    user = ['NoUser','noAuthCodeFound']
    for storedUser in userList:
        if name.lower() in storedUser.lower():
            user = storedUser.split(':')
            user[1] = user[1][:-1]
            break
    return user

def removeFromFile(authCode):
    checkAuthFile()
    with open(visitor_file, 'r+') as f:
        contents = f.readlines()
        f.seek(0)
        for item in contents:
            if authCode not in item:
                f.write(item)
        f.truncate()

if __name__ == '__main__':
    if(len(sys.argv) == 1):
        print('Add User:    python visitor_access_manager.py add <name>')
        print('Delete User: python visitor_access_manager.py del <name>')
        print('Show User:   python visitor_access_manager.py show <name>')

    else:
        if(sys.argv[1] == 'add'):
            if(len(sys.argv) == 2):
                name=raw_input('What is the name of the new user? ')
            else:
                name=''
                i=2
                for arg in sys.argv[2:]:
                    name=name + ' ' + arg
                name=name[1:]
            userFromList=searchForUser(name, readFileContents())
            if(userFromList[1] != 'noAuthCodeFound'):
                print('User already exists, try this argument: visitor_access_manager.py show ' + name)
            else:
                auth=addUser(name)
                print(name + '\'s link is: ' + protocol + hostname + '/?' + parameter + '=' + auth)
                # Code to email person here
                while 1:
                    answer = raw_input("Do you want to send an email? (y/n) ").lower()
                    if answer == "y":
                        email = raw_input("Enter the email address/text address: ")
                        sendEmail(email, protocol + hostname + '/?' + parameter + '=' + auth)
                        break 

        elif(sys.argv[1] == 'del'):
            if(len(sys.argv) == 2):
                name=raw_input('Who should be removed from the list? ')
            else:
                name=''
                i=2
                for arg in sys.argv[2:]:
                    name=name + ' ' + arg
                name=name[1:]
            userFromList=searchForUser(name, readFileContents())
            if(userFromList[1] != 'noAuthCodeFound'):
                removeFromFile(userFromList[1])
                print('Removed ' + userFromList[0] + ' from the authorization file')
            else:
                print('No Match found. Please  try another name.')


        elif(sys.argv[1] == 'show'):
            if(len(sys.argv) == 2):
                name=raw_input('Show which user? ')
            else:
                name=''
                i=2
                for arg in sys.argv[2:]:
                    name=name + ' ' + arg
                name=name[1:]
            userFromList=searchForUser(name, readFileContents())
            if(userFromList[1] != 'noAuthCodeFound'):
                print(userFromList[0] + '\'s link is: ' + protocol + hostname + '/?' + parameter + '=' + userFromList[1])
            else:
                print('No Match found. Please try another name.')
