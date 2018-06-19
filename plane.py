from AStar import node
import random

class plane:
    def __init__(self,no,type,x,y,z,value,load_weight,remain_electricity,capacity,charge):
        self.position=node(x,y,z)
        self.nextposition=node(x,y,z)
        self.no=no
        self.type=type
        self.value=value
        self.load_weight=load_weight
        self.remain_electricity=remain_electricity
        self.capacity=capacity
        self.charge=charge
        self.missionValue=0
        self.status=0
        self.missionStatu=5    # 0起飞 1运输 2攻击 3降落 4选择任务  5充电 (进入降落模式，需要设定货物的目的地)
        self.target=node(0,0,0)
        self.attackTargetNo=-1
        self.goods_no=-1
        self.willGoods_no=-1
        self.targetPlane_no=-1
        self.goods_weight=-1
    def __lt__(self, other):
        return 0
    def reduce_electricity(self):
        self.remain_electricity=self.remain_electricity-self.goods_weight
    def setGoodsWeight(self,goods_weight):
        self.goods_weight=goods_weight
    def chargeing(self):
        self.remain_electricity=self.capacity if self.remain_electricity+self.charge>=self.capacity else self.remain_electricity+self.charge
    def setAttackTargetNo(self,no):
        self.attackTargetNo=no
    def setMissionStatu(self,missionStatu):  # 0起飞 1运输 2攻击 3降落 4选择任务  5充电 6随机飞状态 7攻击高价值敌机 (进入降落模式，需要设定货物的目的地)
        self.missionStatu=missionStatu
    def setstatus(self,statu):
        self.status=statu
    def setWillGoods_no(self,no):
        self.willGoods_no=no
    def landingAndTake(self):
        if self.position.z==1:
            self.setMissionStatu(1)
            self.setgoods_no(self.willGoods_no)
            self.reduce_electricity()
            self.position.z -= 1
        elif self.position.z==0:
            self.setMissionStatu(1)
            self.setgoods_no(self.willGoods_no)
            self.reduce_electricity()
        else:
            self.position.z -= 1
    def takeOff(self,h_low):
        if self.position.z==h_low-1:
            self.position.z += 1
            self.setMissionStatu(4)
        else:
            self.position.z+=1
    def landing(self):
        self.position.z-=1
    def setTarget(self,x,y,z):
        self.target=node(x,y,z)
    def fly(self):
        self.position=self.nextposition
    def nextFly(self,node):
        self.nextposition=node
    def setValue(self,v):
        self.value=v
    def setgoods_no(self,no):
        self.goods_no=no
    def move(self,node):
        self.position=node


def findPlane(plane,MatchStatus):
    for index,i in enumerate(MatchStatus):
        if plane.no==i["no"]:
            return index

def randomFly(position,map,h_low,h_high,parking_x,parking_y,no,myNUm,time):
    directions = [[1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [1, 1, 0], [-1, -1, 0], [1, -1, 0], [-1, 1, 0], [0, 0, 1], \
                [0, 0, -1]]
    if myNUm<30 and position.z<h_low:
        return node(position.x,position.y,position.z+1)
    if myNUm>=30 and no%2 and position.z<h_low+1:
        return node(position.x, position.y, position.z + 1)
    if myNUm>=30 and position.z<h_low:
        return node(position.x, position.y, position.z + 1)

    if position.z>=h_low and position.z<=h_high:
        w=0
        fourPoint=[node(int(map.shape[0]/5)-w,int(map.shape[1]/5)-w,h_low),node(4*int(map.shape[0]/5)+w,int(map.shape[1]/5)-w,h_low), \
                   node(4*int(map.shape[0]/5)+w,3*int(map.shape[1]/5)+w,h_low),node(int(map.shape[0] / 5) - w, 4*int(map.shape[1] / 5) + w, h_low)]
        b=int(time/30)%4
        a=(no+b)%4
        probability=fourPoint[a]-position
        if probability[0]>0 and probability[1]==0:
            a=0
        elif probability[0]<0 and probability[1]==0:
            a=1
        elif probability[0]==0 and probability[1]>0:
            a=2
        elif probability[0]==0 and probability[1]<0:
            a=3
        elif probability[0]>0 and probability[1]>0:
            a=4
        elif probability[0] < 0 and probability[1] < 0:
            a=5
        elif probability[0] > 0 and probability[1] < 0:
            a=6
        elif probability[0] < 0 and probability[1] > 0:
            a=7

        dir=[0, 1, 2, 3, 4, 5, 6, 7]+[a]*16
        random.shuffle(dir)
        for i in range(24):
            if position.x+directions[dir[i]][0]>=0 and position.x+directions[dir[i]][0]<map.shape[0] \
                and position.y+directions[dir[i]][1]>=0 and position.y+directions[dir[i]][1]<map.shape[1]\
                    and position.x+directions[dir[i]][0]!=parking_x and position.y+directions[dir[i]][1]!=parking_y:
                if map[position.x+directions[dir[i]][0]][position.y+directions[dir[i]][1]][position.z+directions[dir[i]][2]]!=1:
                    return node(position.x+directions[dir[i]][0],position.y+directions[dir[i]][1],position.z+directions[dir[i]][2])
    return position

def dodge(position,map,h_low,h_high,nowPosition):
    if position.z >= h_low and position.z <= h_high:
        direction=[nowPosition.x-position.x,nowPosition.y-position.y,nowPosition.z-position.z]
        if direction[0]!=0 and direction[1]!=0 and direction[2]==0:
            if random.randint(0, 1) and map[position.x][position.y + direction[1]][position.z]!=1:
                return node(position.x, position.y + direction[1],position.z)
            elif map[position.x+ direction[0]][position.y][position.z]!=1:
                return node(position.x + direction[0], position.y,position.z)
        if direction[0]!=0 and direction[2]==0:
            if random.randint(0, 1) and position.y + 1 < map.shape[1] and map[position.x+ direction[0]][position.y + 1][position.z]!=1:
                    return node(position.x + direction[0], position.y + 1, position.z)
            elif position.y - 1 >= 0 and map[position.x+ direction[0]][position.y - 1][position.z]!=1:
                    return node(position.x + direction[0], position.y - 1, position.z)
        if direction[1]!=0 and direction[2]==0:
            if random.randint(0, 1) and position.x + 1 < map.shape[0] and map[position.x+1][position.y+ direction[1]][position.z]!=1:
                    return node(position.x + 1, position.y + direction[1], position.z)
            elif position.x - 1 >= 0 and map[position.x-1][position.y+ direction[1]][position.z]!=1:
                    return node(position.x - 1, position.y + direction[1], position.z)
    return position



def finaDecision(planeFlyList,map,h_low,h_high):
    for i in range(50):
        flag = True
        # 检查交叉碰撞
        for i in range(len(planeFlyList) - 1):
            prePosition = planeFlyList[i][0]
            nowPosition = planeFlyList[i][1]
            for j in range(i + 1, len(planeFlyList)):
                if prePosition == planeFlyList[j][1] and nowPosition == planeFlyList[j][0]:
                    # 随机飞一下
                    planeFlyList[i][1] = dodge(prePosition, map, h_low, h_high,nowPosition)
                    flag = False
        # 检查普通碰撞
        for i in range(len(planeFlyList) - 1):
            prePosition = planeFlyList[i][0]
            nowPosition = planeFlyList[i][1]
            for j in range(i + 1, len(planeFlyList)):
                if nowPosition == planeFlyList[j][1] or (prePosition + nowPosition) == (
                        planeFlyList[j][1] + planeFlyList[j][0]):
                    planeFlyList[i][1] = dodge(prePosition, map, h_low, h_high,nowPosition)
                    flag = False
        if flag == True:
            return planeFlyList

    return planeFlyList