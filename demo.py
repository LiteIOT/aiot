# -*- coding: utf-8 -*-
from SimServer import Env
#from Watcher import Watcher
import time
import os
import random
import struct  

#watch = Watcher()
env = Env('127.0.0.1')

counter = 0
#print(env.ip.title())
while True:
    try:
       
        print("-------------------------------------------")
        print("倒计时：", env.countdown)
        print("AI_0与敌人0距离：", env.distance[0][0])
        print("AI_0生命值：", env.ai[0].life)
        print("AI_0子弹数：", env.ai[0].bullet)
        print("AI_0坐标X", env.ai[0].x)
        print("AI_0坐标Y", env.ai[0].y)
        print("AI_0枪口热量", env.ai[0].heat)
        print("AI_0剩余加成时间", env.ai[0].bonus_time)

        print("AI_1生命值：", env.ai[1].life)
        print("AI_1子弹数：", env.ai[1].bullet)
        print("AI_1坐标X", env.ai[1].x)
        print("AI_1坐标Y", env.ai[1].y)
        print("AI_1枪口热量", env.ai[1].heat)
        print("AI_1剩余加成时间", env.ai[1].bonus_time)

        print("Enemy_0生命值：", env.enemy[0].life)
        print("Enemy_0子弹数：", env.enemy[0].bullet)
        
       
        print("Enemy_0坐标X", env.enemy[0].x)
        print("Enemy_0坐标Y", env.enemy[0].y)
        print("Enemy_0剩余加成时间", env.enemy[0].bonus_time)

        print("Enemy_1生命值：", env.enemy[1].life)
        print("Enemy_1子弹数：", env.enemy[1].bullet)
       
        print("Enemy_1坐标X", env.enemy[1].x)
        print("Enemy_1坐标Y", env.enemy[1].y)
        print("Enemy_1剩余加成时间", env.enemy[1].bonus_time)

        
        
        #if env.ai[0].life == 0 or env.countdown == 0:
        #    env.reset()
        x = random.uniform(0, 8)
        y = random.uniform(0, 5)
        time.sleep(2)
        pass

        #env.reset()   #复位命令
        if env.distance[0][1]<2.5:  #与二号敌人小于2.5米射击
            env.follow(env.ai[0].id, env.enemy[1].id)   #AI_1跟踪敌人enemy_2
            env.shooting(env.ai[0].id, True)    #代表编号  射击命令
        else:
            env.shooting(env.ai[0].id, False)
        
        
        env.shooting(env.enemy[1].id, True)

        env.move_to_bonus(env.ai[0].id)  #进入加成去
        env.move_to_supplier(env.ai[1].id)  #进入补弹区，30秒生成一次子弹

        if counter<8:
            counter += 1
            env.move_to_bonus(env.enemy[0].id)  #进入加成去
        else:
            counter += 1
            print( 'counter' + str(counter) )
            env.moveto(env.enemy[0].id, x, y)


        env.move_to_supplier(env.enemy[1].id)  #进入补弹区，30秒生成一次子弹
        

    except KeyboardInterrupt:
        print("Exit")
        env.is_live = False
        os._exit(0) 


