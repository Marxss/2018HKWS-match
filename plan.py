from AStar import *
import copy
from plane import *
from mission import *



def checkParking(pstMatchStatus,pstMapInfo):
    parkingX = pstMapInfo["parking"]["x"]
    parkingY = pstMapInfo["parking"]["y"]
    UAV_price = pstMapInfo["UAV_price"]
    mostplane_weight=0
    mostplane_value = 0
    mostplane=0
    for i in pstMatchStatus["UAV_we"]:
        if i["x"]==parkingX and i["y"]==parkingY and i["z"]==0:
            for j in UAV_price:
                if j["type"]==i["type"] and j["load_weight"]>mostplane_weight:
                    mostplane=i
                    mostplane_weight=j["load_weight"]
                    mostplane_value=j["value"]
    return mostplane,mostplane_weight,mostplane_value

def checkPlaneValid(no,planes):
    for i in planes:
        if i["no"]==no:
            if i["status"]!=1:
                return True
            else:
                print("%s no plane falls" %no)
                return False
    print("don't find %s no plane" %no)
    return False

def NoNotIn(no,planeList):
    flag=True
    for i in planeList:
        if i.no==no:
            flag=False
            break
    return flag

def missionPriority(plane):
    # 0起飞 1运输 2攻击 3降落 4选择任务  5充电 6随机飞 7攻击高价值敌机 (进入降落模式，需要设定货物的目的地)
    if plane.missionStatu==3:
        return 30
    elif plane.missionStatu==1:
        return 25
    elif plane.missionStatu==7:
        return 22
    elif plane.missionStatu==2:
        return 20
    elif plane.missionStatu==4:
        return 18
    elif plane.missionStatu==6:
        return 17
    elif plane.missionStatu==0:
        return 15
    elif plane.missionStatu==5:
        return 10

def findEnemyValue(position,UAV_enemy,h_low):
    for i in UAV_enemy:
        if position.x==i["x"] and position.y==i["y"] and i["z"]<h_low:
            return i["type"]
    return 0



def AlgorithmCalculationFun(mymap,planeList,hadmissionList,pstMatchStatus,pstMapInfo,priceList,attackMissionList,\
                            needElectricityDic,hadAttackMissionDic,priceDic,startAttackNo):
    # for i in pstMatchStatus["UAV_we"]:
    #     print(i)
    # print()

    # # 检查飞机状态
    # for item in planeList:
    #     if not checkPlaneValid(item.no, pstMatchStatus["UAV_we"]):
    #         planeList.remove(item)

    # 初始计算
    print("value:",pstMatchStatus["we_value"])
    enemyNum = len(pstMatchStatus["UAV_enemy"])
    myNUm = len(planeList)
    mySendMatchStatus=copy.deepcopy(pstMatchStatus["UAV_we"])
    # 初始化飞机，检查停机坪
    parkingX = pstMapInfo["parking"]["x"]
    parkingY = pstMapInfo["parking"]["y"]
    UAV_price = pstMapInfo["UAV_price"]
    for i in pstMatchStatus["UAV_we"]:
        if i["x"] == parkingX and i["y"] == parkingY and i["z"] == 0 and NoNotIn(i["no"],planeList):
            for j in UAV_price:
                if j["type"] == i["type"]:
                    planeList.append(plane(i["no"],i["type"],i["x"],i["y"],i["z"],j["value"],j["load_weight"],\
                                           i["remain_electricity"],j["capacity"],j["charge"]))

    # 验证执行攻击任务的我方飞机是否存活  and 任务时间-1
    for i in hadAttackMissionDic.keys():
        hadAttackMissionDic[i].left_time_1()

    for i in pstMatchStatus["UAV_we"]:
        if i["status"]==1 and not NoNotIn(i["no"],planeList):
            for j in planeList:
                if j.no==i["no"]:
                    if j.missionStatu==2 and j.attackTargetNo in hadAttackMissionDic.keys():
                        attackMissionList.append(hadAttackMissionDic[j.attackTargetNo])
                        del hadAttackMissionDic[j.attackTargetNo]
                        # print("%s no liberate mission" %j.no)
                    if j.missionStatu==7:
                        startAttackNo.remove(j.attackTargetNo)
                    break


    # 检查飞机状态  状态6变为4
    for item in planeList:
        if not checkPlaneValid(item.no,pstMatchStatus["UAV_we"]):
            planeList.remove(item)
        if item.missionStatu==6:
            item.setMissionStatu(4)
    planeList.sort(key=lambda x: x.load_weight)
    planeList.sort(key=lambda x: x.remain_electricity)

    # 开局追杀
    enemyList = copy.deepcopy(pstMatchStatus["UAV_enemy"])
    enemyList.sort(key=lambda x: priceDic[x["type"]], reverse=True)
    for i in enemyList:
        if i["type"]!=priceList[0][3] and i["no"] not in startAttackNo and i["x"]!=-1:
            for j in planeList:
                if j.type==priceList[0][3] and (j.missionStatu==4 or j.missionStatu==0):
                    j.setAttackTargetNo(i["no"])
                    j.setTarget(i["x"],i["y"],i["z"])
                    j.setMissionStatu(7)  # 7攻击高价值敌机
                    startAttackNo.append(i["no"])
                    print("%s no flow %s no" %(j.no,j.attackTargetNo))
                    break
                if j.type!=priceList[0][3]:
                    break
        if i["type"]==priceList[0][3]:
            break
    # 检查高价值敌机状态
    for i in planeList:
        if i.missionStatu==7:
            flag=True
            for j in pstMatchStatus["UAV_enemy"]:
                if j["no"]==i.attackTargetNo:
                    flag=False
                    break
            if flag:
                i.setMissionStatu(4)


    # 拷贝一份原始飞机位置表
    prePlaneList=copy.deepcopy(planeList)

    # 更新运输任务的耗电字典
    for i in pstMatchStatus["goods"]:
        if i["no"] not in needElectricityDic.keys():
            needElectricityDic[i["no"]]=(len(a_star(node(i["start_x"],i["start_y"],0),node(i["end_x"],i["end_y"],0),\
                                                    mymap,pstMapInfo["h_low"],pstMapInfo["h_high"]))+2)*i["weight"]

    # 更新到最新的运输任务
    updateMissionList=[]
    hadTakeMissionList=[]
    # 去除高价值敌机要取的货物
    enemyWillGoods=[]
    for i in pstMatchStatus["UAV_enemy"]:
        if i["no"] in startAttackNo and i["status"]!=2 and i["z"]<pstMapInfo["h_low"]:
            for j in pstMatchStatus["goods"]:
                if j["start_x"]==i["x"] and j["start_y"]==i["y"]:
                    enemyWillGoods.append(j["no"])
    for i in pstMatchStatus["goods"]:
        if i["status"]==0 and i["no"] not in enemyWillGoods:
            updateMissionList.append(mission(i["no"],i["start_x"],i["start_y"],i["end_x"],i["end_y"],\
                                                  i["weight"],i["value"],i["start_time"],i["remain_time"],i["left_time"],i["status"],\
                                     1, -1, -1, -1, -1, -1,mymap,pstMapInfo,needElectricityDic))
        elif i["status"]==1:
            hadTakeMissionList.append(mission(i["no"],i["start_x"],i["start_y"],i["end_x"],i["end_y"],\
                                                  i["weight"],i["value"],i["start_time"],i["remain_time"],i["left_time"],i["status"],\
                                     1, -1, -1, -1, -1, -1,mymap,pstMapInfo,needElectricityDic))
    # 删除已有的运输任务
    hadmissionListNo=[]
    for i in hadmissionList:
        hadmissionListNo.append(i.no)
    for i,item in enumerate(updateMissionList):
        if item.no in hadmissionListNo:
            del updateMissionList[i]


    # 验证攻击任务的有效性和 剩余时间-1
    for i in attackMissionList:
        flag = True
        for j in pstMatchStatus["goods"]:
            if j["no"] == i.no:
                flag = False
                break
        if flag:
            attackMissionList.remove(i)
        else:
            i.left_time_1()
    # 检验攻击目标的有效性
    for i in planeList:
        if i.missionStatu==2:
            flag = True
            for j in pstMatchStatus["UAV_enemy"]:
                if j["no"] == i.attackTargetNo:
                    flag = False
                    break
            if flag:
                print("enemy %s has fallen" %i.attackTargetNo)
                i.setMissionStatu(4)

    # 寻找新的攻击任务
    for j in pstMatchStatus["UAV_enemy"]:
        if j["goods_no"]!=-1 and NoNotIn(j["goods_no"],attackMissionList) and NoNotIn(j["goods_no"],hadmissionList) and j["status"]!=2:
            for i in pstMatchStatus["goods"]:
                if i["no"] == j["goods_no"]:
                    attackMissionList.append(mission(i["no"], i["start_x"], i["start_y"], i["end_x"], i["end_y"], \
                                                     i["weight"], i["value"], i["start_time"],i["remain_time"],\
                        len(a_star(node(j["x"], j["y"], j["z"]),node(i["end_x"], i["end_y"], pstMapInfo["h_low"] - 1), \
                                   mymap,pstMapInfo["h_low"], pstMapInfo["h_high"])),  # 剩余路程时间
                                                      i["status"], \
                                                     2, j["no"], j["x"], j["y"], j["z"], j["load_weight"],mymap,pstMapInfo,needElectricityDic))
                    print("find %s plane load %s goods" %(j["no"],i["no"]))
    attackMissionList.sort(key=lambda x:x.totalValue,reverse=True)  # 按价值降序排序


    # 安排任务    # 0起飞 1运输 2攻击 3降落并取货 4选择任务  5充电 (进入降落模式，需要设定货物的目的地和货物编号)
    for i in planeList:
        if i.missionStatu==4:
            index=chooseMission(i,updateMissionList,pstMapInfo,mymap)
            if index!=-1:
                if i.position.x==updateMissionList[index].start_x and i.position.y==updateMissionList[index].start_y \
                        and i.position.z==pstMapInfo["h_low"] and \
                        i.position.z < updateMissionList[index].left_time:
                    if i.type==priceList[0][3]:
                        i.setMissionStatu(3)
                        i.setGoodsWeight(updateMissionList[index].weight)
                        i.setWillGoods_no(updateMissionList[index].no)
                        i.setTarget(updateMissionList[index].end_x,updateMissionList[index].end_y,0)
                        hadmissionList.append(updateMissionList[index])
                    else:
                        enemyType=findEnemyValue(i.position,pstMatchStatus["UAV_enemy"],pstMapInfo["h_low"])
                        if enemyType!=0:
                            for k in priceList:
                                if enemyType==k[3]:
                                    if k[1]<i.value:
                                        hadmissionList.append(updateMissionList[index])
                                    else:
                                        i.setMissionStatu(3)
                                        i.setGoodsWeight(updateMissionList[index].weight)
                                        i.setWillGoods_no(updateMissionList[index].no)
                                        i.setTarget(updateMissionList[index].end_x, updateMissionList[index].end_y, 0)
                                        hadmissionList.append(updateMissionList[index])
                                    break
                        else:
                            i.setMissionStatu(3)
                            i.setGoodsWeight(updateMissionList[index].weight)
                            i.setWillGoods_no(updateMissionList[index].no)
                            i.setTarget(updateMissionList[index].end_x, updateMissionList[index].end_y, 0)
                            hadmissionList.append(updateMissionList[index])

                else:
                    i.move(a_star(i.position,node(updateMissionList[index].start_x,updateMissionList[index].start_y,pstMapInfo["h_low"]-1), \
                                     mymap,pstMapInfo["h_low"],pstMapInfo["h_high"])[0])
                del updateMissionList[index]
            else:
                # 没有安排上运输任务的飞机，开始安排攻击任务
                flag=False
                for j in attackMissionList:
                    if len(a_star(i.position,node(j.end_x,j.end_y,pstMapInfo["h_low"]-1), \
                                     mymap,pstMapInfo["h_low"],pstMapInfo["h_high"]))<j.left_time:
                        i.setAttackTargetNo(j.target_no)
                        i.setMissionStatu(2)
                        i.setTarget(j.end_x, j.end_y, pstMapInfo["h_low"]-1)
                        print("%s no goto attack" %i.no)
                        hadmissionList.append(j)
                        hadAttackMissionDic[i.attackTargetNo]=j
                        attackMissionList.remove(j)
                        flag=True
                        break
                if not flag:
                    i.move(randomFly(i.position, mymap, pstMapInfo["h_low"], pstMapInfo["h_high"], \
                                     pstMapInfo["parking"]["x"],pstMapInfo["parking"]["y"],i.no,myNUm,pstMatchStatus["time"]))
                    i.setMissionStatu(6)


    # 有任务的飞机执行move（）   # 0起飞 1运输 2攻击 3降落并取货 4选择任务  5 充电  6随机飞  7攻击高价值敌机 (进入降落模式，需要设定货物的目的地)
    for i in planeList:
        if i.missionStatu == 5:
            i.chargeing()
        elif i.missionStatu == 0:
            i.takeOff(pstMapInfo["h_low"])
        elif i.missionStatu==1:
            i.move(a_star(i.position,i.target,mymap,pstMapInfo["h_low"],pstMapInfo["h_high"])[0])
            i.reduce_electricity()
            if i.position==i.target:
                i.setMissionStatu(0)
        elif i.missionStatu ==2 and i.position!=i.target:
            i.move(a_star(i.position, i.target, mymap, pstMapInfo["h_low"], pstMapInfo["h_high"])[0])
            print("%s no goto attack %s no" %(i.no,i.attackTargetNo))
        elif i.missionStatu ==2 and i.position==i.target:
            print("%s no plane waiting %s no" %(i.no,i.attackTargetNo))
        elif i.missionStatu == 3 and i.position.z!=1:
            i.landingAndTake()
        elif i.missionStatu == 3 and i.position.z==1:
            flag=False
            for j in pstMatchStatus["UAV_enemy"]:
                if j["x"]==i.position.x and j["y"]==i.position.y and j["z"]==0 or mymap[i.position.x][i.position.y][0]==2:
                    flag=True
                    break
            if flag:
                i.position.z = 0
            else:
                i.landingAndTake()
        elif i.missionStatu == 7:
            if i.position.x==pstMapInfo["parking"]["x"] and i.position.y==pstMapInfo["parking"]["y"] and i.position.z==0:
                i.chargeing()
            for j in pstMatchStatus["UAV_enemy"]:
                if j["no"]==i.attackTargetNo:
                    if j["x"]!=-1:
                        i.setTarget(j["x"],j["y"],j["z"])
                        flyPath=a_star(i.position, i.target, mymap, pstMapInfo["h_low"], pstMapInfo["h_high"])
                        if j["z"]<pstMapInfo["h_low"] and 2*pstMapInfo["h_low"] < len(flyPath):
                            for k in pstMatchStatus["goods"]:
                                if k["start_x"]==j["x"] and k["start_y"]==j["y"]:
                                    if len(a_star(node(k["start_x"],k["start_y"],0),node(k["end_x"],k["end_y"],0),mymap,pstMapInfo["h_low"],pstMapInfo["h_high"]))\
                                        +j["z"] > len(a_star(i.position,node(k["end_x"],k["end_y"],0),mymap, pstMapInfo["h_low"], pstMapInfo["h_high"])):
                                        i.setTarget(k["end_x"],k["end_y"],pstMapInfo["h_low"]-1)
                                        i.setMissionStatu(2)
                                        hadmissionList.append(mission(k["no"], k["start_x"], k["start_y"], k["end_x"], k["end_y"], \
                                                     k["weight"], k["value"], k["start_time"],k["remain_time"],\
                                        len(a_star(node(k["start_x"],k["start_y"],0),node(k["end_x"],k["end_y"],0), \
                                        mymap,pstMapInfo["h_low"], pstMapInfo["h_high"]))+j["z"],  # 剩余路程时间
                                                      k["status"], \
                                                     2, j["no"], j["x"], j["y"], j["z"], j["load_weight"],mymap,pstMapInfo,needElectricityDic))
                                    break
                    break
            if i.position!=i.target:
                i.move(a_star(i.position, i.target, mymap, pstMapInfo["h_low"], pstMapInfo["h_high"])[0])
                print("%s no flow %s no" % (i.no, i.attackTargetNo))
            else:
                print("%s no start waiting %s no" % (i.no, i.attackTargetNo))

    # 充满电的飞机准备起飞
    for i in sorted(planeList,key=lambda x:x.load_weight,reverse=True):
        if i.missionStatu ==5 and i.remain_electricity==i.capacity:
            i.setMissionStatu(0)
            break


    # 处理自我碰撞问题
    planFlyList=[]
    for i in range(len(planeList)):
        planFlyList.append([prePlaneList[i].position,planeList[i].position,missionPriority(planeList[i]),planeList[i].no])
        planFlyList.sort(key=lambda x:x[2])
    copyPlanFlyList=copy.deepcopy(planFlyList)
    weFly=finaDecision(copyPlanFlyList,mymap,pstMapInfo["h_low"],pstMapInfo["h_high"])
    for i in range(len(planeList)):
        for j in range(len(weFly)):
            if planeList[i].no==weFly[j][3]:
                planeList[i].move(weFly[j][1])
        
    # 处理即将发送的数据
    for i in planeList:
        if i.missionStatu == 1 and i.position.z==0:
            index=findPlane(i,mySendMatchStatus)
            mySendMatchStatus[index]["z"]=0
            mySendMatchStatus[index]["goods_no"]=i.willGoods_no
            mySendMatchStatus[index]["remain_electricity"]=i.remain_electricity
        else:
            index = findPlane(i, mySendMatchStatus)
            mySendMatchStatus[index]["x"] = i.position.x
            mySendMatchStatus[index]["y"] = i.position.y
            mySendMatchStatus[index]["z"] = i.position.z
            mySendMatchStatus[index]["remain_electricity"] = i.remain_electricity

    # 最终结果处理
    res=[]
    for i in mySendMatchStatus:
        if i["status"]!=1:
            res.append(i)

    # 买飞机
    purchase_UAV=[]
    purchase_dic={}
    if pstMatchStatus["we_value"]>=priceList[0][1]:
        print("myPlaneNum:",myNUm)
        if myNUm<2*enemyNum or myNUm<10:
            purchase_dic["purchase"]=priceList[0][2]["type"]
            purchase_UAV.append(purchase_dic)
        else:
            average_weight=0
            goodsNUm=0
            for i in pstMatchStatus["goods"]:
                if i["status"]==0:
                    average_weight+=i["weight"]
                    goodsNUm+=1
            if goodsNUm:
                average_weight=average_weight/goodsNUm
            for i in priceList:
                if i[0]>average_weight:
                    if pstMatchStatus["we_value"]>=i[1]:
                        purchase_dic["purchase"]=i[2]["type"]
                        purchase_UAV.append(purchase_dic)
                    break
            if not purchase_dic:
                purchase_dic["purchase"] = priceList[0][2]["type"]

    return res,purchase_UAV