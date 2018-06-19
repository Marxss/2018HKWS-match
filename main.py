# -*- coding:utf-8 -*-
import sys
import socket
import json
import numpy as np
from plan import AlgorithmCalculationFun
#从服务器接收一段字符串, 转化成字典的形式
def RecvJuderData(hSocket):
    nRet = -1
    Message = hSocket.recv(1024 * 1024 * 4)
    # print(Message)
    len_json = int(Message[:8])
    str_json = Message[8:].decode()
    while len(str_json)!=len_json:
        Message = hSocket.recv(1024 * 1024 * 4)
        str_json=str_json+Message.decode()
    nRet = 0
    Dict = json.loads(str_json)

    return nRet, Dict

# 接收一个字典,将其转换成json文件,并计算大小,发送至服务器
def SendJuderData(hSocket, dict_send):
    str_json = json.dumps(dict_send)
    len_json = str(len(str_json)).zfill(8)
    str_all = len_json + str_json
    # print(str_all)
    ret = hSocket.sendall(str_all.encode())
    if ret == None:
        ret = 0
    # print('sendall', ret)
    return ret

#绘制地图
def writeMap(mapdata):
    x = mapdata["map"]["x"]
    y = mapdata["map"]["y"]
    z = mapdata["map"]["z"]
    mymap=np.array([0]*(x*y*z)).reshape(x,y,z)
    fog = mapdata["fog"]
    for i in range(len(fog)):
        x = fog[i]["x"]
        y = fog[i]["y"]
        l = fog[i]["l"]
        w = fog[i]["w"]
        b = fog[i]["b"]
        t = fog[i]["t"]
        for i in range(x, x + l):
            for j in range(y, y + w):
                for k in range(b, t + 1):
                    mymap[i][j][k] = 2
    building=mapdata["building"]
    for i in range(len(building)):
        x = building[i]["x"]
        y = building[i]["y"]
        l = building[i]["l"]
        w = building[i]["w"]
        h = building[i]["h"]
        for i in range(x,x+l):
            for j in range(y,y+w):
                for k in range(0,h):
                    mymap[i][j][k]=1

    return mymap



# #用户自定义函数, 返回字典FlyPlane, 需要包括 "UAV_info", "purchase_UAV" 两个key.
# def AlgorithmCalculationFun(initmap,data):
#
#     return 0





def main(szIp, nPort, szToken):
    print("server ip %s, prot %d, token %s\n", szIp, nPort, szToken)

    #Need Test // 开始连接服务器
    hSocket = socket.socket()

    hSocket.connect((szIp, nPort))

    #接受数据  连接成功后，Judger会返回一条消息：
    nRet, _ = RecvJuderData(hSocket)
    if (nRet != 0):
        return nRet
    

    # // 生成表明身份的json
    token = {}
    token['token'] = szToken        
    token['action'] = "sendtoken"   

    
    #// 选手向裁判服务器表明身份(Player -> Judger)
    nRet = SendJuderData(hSocket, token)
    if nRet != 0:
        return nRet

    #//身份验证结果(Judger -> Player), 返回字典Message
    nRet, Message = RecvJuderData(hSocket)
    if nRet != 0:
        return nRet
    
    if Message["result"] != 0:
        print("token check error\n")
        return -1

    # // 选手向裁判服务器表明自己已准备就绪(Player -> Judger)
    stReady = {}
    stReady['token'] = szToken
    stReady['action'] = "ready"

    nRet = SendJuderData(hSocket, stReady)
    if nRet != 0:
        return nRet

    # //对战开始通知(Judger -> Player)
    nRet, Message = RecvJuderData(hSocket)
    if nRet != 0:
        return nRet
    
    #初始化地图信息
    pstMapInfo = Message["map"]
    mymap=writeMap(pstMapInfo)
    
    #初始化比赛状态信息
    pstMatchStatus = {}
    pstMatchStatus["time"] = 0

    #初始化飞机状态信息
    pstFlayPlane = {}
    pstFlayPlane["nUavNum"] = len(pstMapInfo["init_UAV"])
    pstFlayPlane["astUav"] = []

    #每一步的飞行计划
    FlyPlane_send = {}
    FlyPlane_send["token"] = szToken
    FlyPlane_send["action"] = "flyPlane"

    for i in range(pstFlayPlane["nUavNum"]):
        pstFlayPlane["astUav"].append(pstMapInfo["init_UAV"][i])

    #发送第一次飞行计划
    FlyPlane_send['UAV_info'] = pstFlayPlane["astUav"]
    print(pstMatchStatus["time"])
    # //发送飞行计划
    nRet = SendJuderData(hSocket, FlyPlane_send)
    if nRet != 0:
        return nRet
    # 获取飞机价格表
    priceList=[]
    priceDic={}
    for i in pstMapInfo["UAV_price"]:
        priceList.append((i["load_weight"],i["value"],i,i["type"]))
        priceDic[i["type"]]=i["value"]
    priceList.sort()
    for i in priceList:
        print(i)
    # // 根据服务器指令，不停的接受发送数据
    planeList = []
    hadmissionList=[]
    attackMissionList=[]
    needElectricityDic={}
    hadAttackMissionDic={}
    startAttackNo=[]
    while True:
        
        # // 接受当前比赛状态
        nRet, pstMatchStatus = RecvJuderData(hSocket)
        if nRet != 0:
            return nRet
        
        if pstMatchStatus["match_status"] == 1:
            print("game over, we value %d, enemy value %d\n", pstMatchStatus["we_value"], pstMatchStatus["enemy_value"])
            hSocket.close()
            return 0

        # // 进行当前时刻的数据计算, 填充飞行计划
        FlyPlane,purchase_UAV= AlgorithmCalculationFun(mymap,planeList,hadmissionList,pstMatchStatus,pstMapInfo,\
                                                       priceList,attackMissionList,needElectricityDic,hadAttackMissionDic,priceDic,startAttackNo)
        print()
        for i in FlyPlane:
            print(i)
        FlyPlane_send['UAV_info'] = FlyPlane
        FlyPlane_send["purchase_UAV"]=purchase_UAV

        # print(pstMatchStatus["time"])
        # //发送飞行计划
        nRet = SendJuderData(hSocket, FlyPlane_send)
        if nRet != 0:
            return nRet

if __name__ == "__main__":
    if len(sys.argv) == 4:
        print("Server Host: " + sys.argv[1])
        print("Server Port: " + sys.argv[2])
        print("Auth Token: " + sys.argv[3])
        main(sys.argv[1], int(sys.argv[2]), sys.argv[3])
    else:
        host="39.107.126.155"
        port=30918
        token="fd1bd2f3-44b4-44a7-ac6c-ecde1a8f2ac8"
        main(host,port,token)
        print("need 3 arguments")