#!/usr/bin/python

import string
import random
import sys
import os.path

import smtplib
import email
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText

USERNAME = ""
PASSWORD = ""
FROM_ADDR = ""

authFile='visitors.txt'
protocol='http://'
hostname=''
authParameterName='visitor'

def sendEmail(e, l):
    SUBJECT = "Visitor"
    BODY = "Visit the following link to open the gate: "
    link = l
    msg = MIMEMultipart()
    msg['From'] = FROM_ADDR
    msg['to'] = e
    msg['Subject'] = SUBJECT
    msg.attach(MIMEText(BODY + l))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(USERNAME, PASSWORD)
    server.sendmail(FROM_ADDR, e, msg.as_string())
    server.quit()


def constructAuth():
    potentialData='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890'
    auth=''.join(random.choice(potentialData) for _ in xrange(16))
    return auth

def checkAuthFile():
    if not os.path.exists(authFile):
        file(authFile, 'w').close()

def addUser(name):
    checkAuthFile()
    with open(authFile, 'a') as f:
        auth=constructAuth()
        f.write(name + ':' + auth + '\n')
        print(name + ' Added to the file with auth key ' + auth)
        return auth

def readFileContents():
    checkAuthFile()
    with open(authFile, 'r') as f:
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
    with open(authFile, 'r+') as f:
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
                print(name + '\'s link is: ' + protocol + hostname + '/?' + authParameterName + '=' + auth)
                # Code to email person here
                while 1:
                    answer = raw_input("Do you want to send an email? (y/n) ").lower()
                    if answer == "y":
                        email = raw_input("Enter the email address/text address: ")
                        sendEmail(email, protocol + hostname + '/?' + authParameterName + '=' + auth)
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
                print(userFromList[0] + '\'s link is: ' + protocol + hostname + '/?' + authParameterName + '=' + userFromList[1])
            else:
                print('No Match found. Please try another name.')
