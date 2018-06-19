from AStar import *

class mission:
    def __init__(self,no,start_x,start_y,end_x,end_y,weight,value,start_time,remain_time,left_time,status,type, \
            target_no,target_x,target_y,target_z,planeValue,mymap,pstMapInfo,needElectricityDic ):
        self.no=no
        self.start_x=start_x
        self.start_y=start_y
        self.end_x=end_x
        self.end_y=end_y
        self.weight=weight
        self.value=value
        self.start_time=start_time
        self.remain_time=remain_time
        self.left_time=left_time
        self.status=status
        self.type=type  # 1 货物运输任务 2 攻击任务
        self.target_no = target_no  # 敌机号
        self.target_x = target_x
        self.target_y = target_y
        self.target_z = target_z
        self.totalValue = planeValue + self.value
        self.needElectricity=needElectricityDic[self.no]
            #(len(a_star(node(self.start_x,self.start_y,0),node(self.end_x,self.end_y,0),mymap,pstMapInfo["h_low"],pstMapInfo["h_high"]))+2)*self.weight

    def left_time_1(self):
        self.left_time-=1

    def __eq__(self, other):
        if self.no == other.no and self.start_x == other.start_x and self.start_y == other.start_y\
        and self.end_x == other.end_x\
        and self.end_y == other.end_y\
        and self.start_time == other.start_time:
            return True
        return False
class attackMission:
    def __init__(self,no,target_no,target_x,target_y,target_z,end_x,end_y,planeValue,goodsvalue):
        self.no=no  # 货物号
        self.target_no=target_no  # 敌机号
        self.target_x=target_x
        self.target_y=target_y
        self.target_z=target_z
        self.end_x=end_x
        self.end_y=end_y
        self.value=planeValue+goodsvalue
        self.type=2 #2 攻击任务

def chooseMission(plane, updateMissionList, pstMapInfo, mymap):
    missionIndex = -1
    missionValue = 0
    for index, i in enumerate(updateMissionList):
        if plane.load_weight >= i.weight and \
                max(abs(plane.position.x - i.start_x),
                     abs(plane.position.y - i.start_y)) + plane.position.z + 2 < i.left_time \
            and i.needElectricity < plane.remain_electricity:
                #and (plane.position.z * 2+max(abs(i.end_x - i.start_x), abs(i.end_y - i.start_y)) + 8)*i.weight < plane.remain_electricity:  # 剩余时间阈值
            length = max(abs(plane.position.x - i.start_x),
                         abs(plane.position.y - i.start_y)) + plane.position.z * 3 + \
                     max(abs(i.end_x - i.start_x), abs(i.end_y - i.start_y))
            if i.value / length**1.2 > missionValue and len(a_star(plane.position,node(i.start_x,i.start_y,0),\
                                                    mymap,pstMapInfo["h_low"],pstMapInfo["h_high"]))+2<i.left_time:
                missionValue = i.value / length**1.2
                missionIndex = index
    return missionIndex

def findMission(no, missionList):
    for i in missionList:
        if i.no == no:
            return i

