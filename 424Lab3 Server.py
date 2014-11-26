from tkinter import *
from tkinter.messagebox import *
import time, _thread as thread 
from socket import *

import sqlite3


myHost = '127.0.0.1'
myPort = 50007

class Server():
    def __init__(self):
        serverSock = socket(AF_INET, SOCK_STREAM)
        serverSock.bind((myHost,myPort))
        serverSock.listen(5)
        print('Server is Listening!')

        while True:
            self.db = sqlite3.connect('./mydb.db')
            self.cursor = self.db.cursor()
            try:
                self.db.execute('''CREATE TABLE IF NOT EXISTS
                                   users(name TEXT PRIMARY KEY unique, id TEXT, height TEXT, weight TEXT, bp TEXT)''')
                self.db.execute('''INSERT OR IGNORE INTO users(name, id) VALUES(?,?)''',('test','1234'))
                self.db.commit()
            except Exception as e:
                self.db.rollback()
                raise e

    
            self.connection, self.address = serverSock.accept() 
            print('Server connected by', self.address,'at', self.now())
            while True: 
                command = self.connection.recv(1024).decode()

                print(command)

                if command == 'verify':
                    self.verifyLogin()
                elif command == 'measurement storage':
                    self.storeMeasurement()
                elif command == 'measurement retrieve':
                    self.getMeasurement()
                elif command == 'close':
                    self.connection.close()
                    print('Server is closed')
                    return
        
                if not command: break
                
        self.connection.close()
        return


    def now(self):
        return time.ctime(time.time())

    def verifyLogin(self):
        data = self.connection.recv(1024).decode().split()
        user = data[0]
        pasword = data[1]

        try:
            self.cursor.execute('''SELECT id FROM users WHERE name=?''',(user,))
            result = self.cursor.fetchone()
        except Exception as e:
            self.db.rollback()
            raise e    
        
        if pasword == result[0]:
            print('valid')
            reply='valid'
            self.connection.send(reply.encode())
            self.username = user
        else:
            print('invalid')
            reply='invalid'
            self.connection.send(reply.encode())

    def storeMeasurement(self):
        data = self.connection.recv(1024).decode().split()
        height = data[0]
        weight = data[1]
        bp = data[2]

        try:
            self.db.execute('''UPDATE users SET height=?, weight=?, bp=? WHERE name=?''',(height,weight,bp,self.username))
            self.db.commit()
            print('success')
            reply = 'success'
            self.connection.send(reply.encode())
        except Exception as e:
            self.db.rollback()
            raise e

        
        

    def getMeasurement(self):

        try:
            self.cursor.execute('''SELECT height, weight, bp FROM users WHERE name=?''',(self.username,))
            result = self.cursor.fetchone()
        except Exception as e:
            self.db.rollback()
            raise e

        height = result[0]
        weight = result[1]
        bp = result[2]
        content = ('Height: ' + height + '\n' + 'Weight: ' + weight + '\n' + 'Blood Presure: ' + bp)
        
        reply = content
        self.connection.send(reply.encode())
        print('measurments sent')
        


if __name__ == '__main__':
    Server()
    
