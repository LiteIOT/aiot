# -*- coding: utf-8 -*-
import threading
import time
import os
import struct
#引入模块
from socket import *
import queue

AI_OFFSET_0 = 20
AI_OFFSET_1 = 44
ENEMY_OFFSET_0 = 68
ENEMY_OFFSET_1 = 88

STATUS_HEADER_1 = 0
STATUS_HEADER_2 = 1
STATUS_LENGTH_1 = 2
STATUS_LENGTH_2 = 3
STATUS_BUFFER   = 4

class AICar:
    def __init__(self):
        self.id = 0
        self.life = 0          #生命值，血量
        self.bullet=0          #子弹数
        self.x=0.0               #当前坐标X，单位为米
        self.y=0.0               #当前坐标Y
        self.heat=0               #枪口热量

class Env(object):
    #创建socket
    is_live = True
    #s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client = socket(AF_INET, SOCK_STREAM)
    def __init__(self, ip_address):
        # threading.Thread.__init__(self)
        self.port = 3000       #模拟器端口
        self.ip = ip_address   #模拟器IP地址

        self.ai = [AICar(), AICar()]
        self.enemy = [AICar(), AICar()]
        self.distance = [ [0.0, 0.0], [0.0, 0.0] ] #AI 与敌人1的距离

        self.ai[0].id = 0
        self.ai[0].life = 0          #生命值，血量
        self.ai[0].bullet=0          #子弹数
        self.ai[0].x=0.0               #当前坐标X，单位为米
        self.ai[0].y=0.0               #当前坐标Y
        self.ai[0].heat=0               #枪口热量
        self.ai[0].bonus_time = 0
       

        self.ai[1].id = 1
        self.ai[1].life = 0          #生命值，血量
        self.ai[1].bullet=0          #子弹数
        self.ai[1].x=0.0               #当前坐标X，单位为米
        self.ai[1].y=0.0               #当前坐标Y
        self.ai[1].heat=0               #枪口热量
        self.ai[1].bonus_time = 0
        #self.ai[1].distance[0]=0.0      #与敌人1的距离
        #self.ai[1].distance[1]=0.0     #与敌人2的距离

        self.enemy[0].id = 2  #b'10
        self.enemy[0].life = 0          #生命值，血量
        self.enemy[0].bullet=0          #子弹数
        self.enemy[0].x=0.0               #当前坐标X，单位为米
        self.enemy[0].y=0.0               #当前坐标Y
        self.enemy[0].heat=0               #枪口热量
        self.enemy[0].bonus_time = 0

        self.enemy[1].id = 3  #b'11
        self.enemy[1].life = 0          #生命值，血量
        self.enemy[1].bullet=0          #子弹数
        self.enemy[1].x=0.0               #当前坐标X，单位为米
        self.enemy[1].y=0.0               #当前坐标Y
        self.enemy[1].heat=0               #枪口热量
        self.enemy[1].bonus_time = 0

        self.countdown=0       #剩余时间，单位为秒

        self.queue_buffer = queue.Queue()
        self.buffer_counter = 0
        self.buffer_length  = 0
        self.package = []
        self.tcpstatus = 0
       

        #输出给模拟器
        #self.outX=0
        #self.outY=0
        #self.outShoot=0        #是否射击
        #监听端口
        self.client.connect((self.ip, self.port))
       
        print(self.ip.title())
        print('Waiting for connection...')
        
        self.process()
    
    def reset(self):
        class_id = 1000 #Reset
        data = struct.pack('<2B2h',0x55,0xaa, 2, class_id ) 
        self.client.send(data)
    
    def moveto(self, ai_id, x, z):
        x=x-4
        z=z-2.5
        if x>4:
            x=4
        elif x<-4:
            x=-4

        if z>2.5:
            z=2.5
        elif x<-2.5:
            z=-2.5
        class_id = 1002
        data = struct.pack('<2B3h2i',0x55,0xaa, 12, class_id, ai_id, int(x*1000), int(z*1000) ) 
        self.client.send(data)

    def move_to_supplier(self, ai_id):
        if ai_id>1:
            self.moveto(ai_id, 4.0, 4.5)
        else:
            self.moveto(ai_id, 4.0, 0.5)
    
    def move_to_bonus(self, ai_id):
        if ai_id>1:
            self.moveto(ai_id, 6.3, 2.0)
        else:
            self.moveto(ai_id, 1.7, 3.0)

    def shooting(self, ai_id, s):
        class_id = 1003
        shoot = 0
        if s==True:
            shoot=1
        data = struct.pack('<2B3hi',0x55,0xaa, 8, class_id, ai_id, int(s) )     #按fmt这个格式把后面数据给封装成指定的数据
        
        self.client.send(data)
    
    def follow(self, ai_id, enemy_id):
        class_id = 1001
        data = struct.pack('<2B4h',0x55,0xaa, 6, class_id, ai_id, enemy_id ) 
        self.client.send(data)

    def process(self):
        #args是关键字参数，需要加上名字，写成args=(self,)
        th1 = threading.Thread(target=Env.buildList, args=(self,))
        th1.setDaemon(True)
        th1.start()

        th2 = threading.Thread(target=Env.pingServer, args=(self,))
        th2.setDaemon(True)
        th2.start()

        th3 = threading.Thread(target=Env.unpackServer, args=(self,))
        th3.setDaemon(True)
        th3.start()
        #th1.join()
    
    #print 'data size = %d' % (data_size)
    def pingServer(self):
        while  self.is_live:
            class_id = 999 #ping
            data = struct.pack('<2B2h',0x55,0xaa, 2, class_id ) 
            self.client.send(data)
            time.sleep(0.1)
    
    def unpackServer(self):
        while  self.is_live:
            while not self.queue_buffer.empty():
                c = self.queue_buffer.get()
                #print(c)
                if self.tcpstatus == STATUS_HEADER_1:
                    if c == 85: #0x55
                        
                        self.tcpstatus = STATUS_HEADER_2
                    else:
                        self.tcpstatus = STATUS_HEADER_1

                elif self.tcpstatus == STATUS_HEADER_2:
                    
                    if c == 170: #0xAA
                        self.buffer_length  = 0
                        
                        self.tcpstatus = STATUS_LENGTH_1
                    else:
                        self.tcpstatus = STATUS_HEADER_1

                elif self.tcpstatus == STATUS_LENGTH_1:
                    self.tcpstatus = STATUS_LENGTH_2
                
                elif self.tcpstatus == STATUS_LENGTH_2:
                    self.buffer_length  = c
                    self.buffer_counter = 0
                    self.tcpstatus = STATUS_BUFFER
                
                elif self.tcpstatus == STATUS_BUFFER:
                    self.package.append(c)
                    self.buffer_counter  += 1
                    

                    if self.buffer_counter == self.buffer_length:

                        self.countdown = int.from_bytes(self.package[0:4], byteorder='little')

                        self.distance[0][0] = int.from_bytes(self.package[4:8], byteorder='little')/1000
                        self.distance[0][1] = int.from_bytes(self.package[8:12], byteorder='little')/1000
                        self.distance[1][0] = int.from_bytes(self.package[12:16], byteorder='little')/1000
                        self.distance[1][1] = int.from_bytes(self.package[16:20], byteorder='little')/1000

                        self.ai[0].life = int.from_bytes(self.package[AI_OFFSET_0+0:AI_OFFSET_0+4], byteorder='little')
                        self.ai[0].bullet = int.from_bytes(self.package[AI_OFFSET_0+4:AI_OFFSET_0+8], byteorder='little')
                        self.ai[0].x = int.from_bytes(self.package[AI_OFFSET_0+8:AI_OFFSET_0+12], byteorder='little')/1000
                        self.ai[0].y = int.from_bytes(self.package[AI_OFFSET_0+12:AI_OFFSET_0+16], byteorder='little')/1000
                        self.ai[0].heat = int.from_bytes(self.package[AI_OFFSET_0+16:AI_OFFSET_0+20], byteorder='little')
                        self.ai[0].bonus_time = int.from_bytes(self.package[AI_OFFSET_0+20:AI_OFFSET_0+24], byteorder='little')

                        self.ai[1].life = int.from_bytes(self.package[AI_OFFSET_1+0:AI_OFFSET_1+4], byteorder='little')
                        self.ai[1].bullet = int.from_bytes(self.package[AI_OFFSET_1+4:AI_OFFSET_1+8], byteorder='little')
                        self.ai[1].x = int.from_bytes(self.package[AI_OFFSET_1+8:AI_OFFSET_1+12], byteorder='little')/1000
                        self.ai[1].y = int.from_bytes(self.package[AI_OFFSET_1+12:AI_OFFSET_1+16], byteorder='little')/1000
                        self.ai[1].heat = int.from_bytes(self.package[AI_OFFSET_1+16:AI_OFFSET_1+20], byteorder='little')
                        self.ai[1].bonus_time = int.from_bytes(self.package[AI_OFFSET_1+20:AI_OFFSET_1+24], byteorder='little')
                        
                        self.enemy[0].life = int.from_bytes(self.package[ENEMY_OFFSET_0+0:ENEMY_OFFSET_0+4], byteorder='little')
                        self.enemy[0].bullet = int.from_bytes(self.package[ENEMY_OFFSET_0+4:ENEMY_OFFSET_0+8], byteorder='little')
                        self.enemy[0].x = int.from_bytes(self.package[ENEMY_OFFSET_0+8:ENEMY_OFFSET_0+12], byteorder='little')/1000
                        self.enemy[0].y = int.from_bytes(self.package[ENEMY_OFFSET_0+12:ENEMY_OFFSET_0+16], byteorder='little')/1000
                        self.enemy[0].bonus_time =  int.from_bytes(self.package[ENEMY_OFFSET_0+16:ENEMY_OFFSET_0+20], byteorder='little')

                        self.enemy[1].life = int.from_bytes(self.package[ENEMY_OFFSET_1+0:ENEMY_OFFSET_1+4], byteorder='little')
                        self.enemy[1].bullet = int.from_bytes(self.package[ENEMY_OFFSET_1+4:ENEMY_OFFSET_1+8], byteorder='little')
                        self.enemy[1].x = int.from_bytes(self.package[ENEMY_OFFSET_1+8:ENEMY_OFFSET_1+12], byteorder='little')/1000
                        self.enemy[1].y = int.from_bytes(self.package[ENEMY_OFFSET_1+12:ENEMY_OFFSET_1+16], byteorder='little')/1000
                        self.enemy[1].bonus_time = int.from_bytes(self.package[ENEMY_OFFSET_1+16:ENEMY_OFFSET_1+20], byteorder='little')

                        #print(self.package)
                        self.package = []
                        self.tcpstatus = STATUS_HEADER_1
                    

                



#print 'data size = %d' % (data_size)
    def buildList(self):
        while  self.is_live:
           
           
            #packed_data = s.pack(*values)
            #unpacked_data = s.unpack(packed_data)
            r = self.client.recv(1024)
           
            #print ("[+] recv data", r)
            #print(len(r))
            if len(r) > 0:
                for i in range(len(r)):
                    self.queue_buffer.put(r[i])
            
            else:
               time.sleep(0.1)
         
           



