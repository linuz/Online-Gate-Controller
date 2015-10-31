#!/usr/bin/python

import string, random, sys, os.path

authFile='visitors.txt'
protocol='http://'
hostname=''
authParameterName='visitor'

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
        print('Add User:    python manageUsers.py add <name>')
        print('Delete User: python manageUsers.py del <name>')
        print('Show User:   python manageUsers.py show <name>')

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
                print('User already exists, try this argument: manageUsers.py show ' + name)
            else:
                auth=addUser(name)
                print(name + '\'s link is: ' + protocol + hostname + '/?' + authParameterName + '=' + auth)

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
