import string, random, sys

authFile='visitors.txt'
protocol='http://'
hostname=''
authParameterName='visitor'

def constructAuth():
    potentialData='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890'
    auth=''.join(random.choice(potentialData) for _ in xrange(16))
    return auth

def addUser(name):
    with open(authFile, 'a') as f:
        auth=constructAuth()
        f.write(name + ':' + auth + '\n')
        print(name + ' Added to the file with auth key ' + auth)
        return auth

def readFileContents():
    with open(authFile, 'r') as f:
        fileContents=f.readlines()
        return fileContents

def searchForUser(name, userList):
    match = 'noAuthCodeFound'
    for item in userList:
        if name.lower() in item.lower():
            match = item.split(':')[1]
            match = match[:-1]
            break
    return match

def removeFromFile(authCode):
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
            authSearched=searchForUser(name, readFileContents())
            if(authSearched != 'noAuthCodeFound'):
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
            authSearched=searchForUser(name, readFileContents())
            if(authSearched != 'noAuthCodeFound'):
                removeFromFile(authSearched)
                print('Removed ' + name + ' from the authorization file')
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
            authSearched=searchForUser(name, readFileContents())
            if(authSearched != 'noAuthCodeFound'):
                print(name + '\'s link is: ' + protocol + hostname + '/?' + authParameterName + '=' + authSearched)
            else:
                print('No Match found. Please  try another name.')
