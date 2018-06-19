import heapq

class node:
    def __init__(self,x,y,z):
        self.x=x
        self.y=y
        self.z=z
        # self.score=0
    # def addScore(self,f):
    #     self.score=f
    def __lt__(self, other):
        return 1
    def __eq__(self, other):
        if self.x==other.x and self.y==other.y and self.z==other.z:
            return True
        else:
            return False
    def __hash__(self):
        return hash((self.x,self.y,self.z))
    def __repr__(self):
        return '%s,'%self.x+'%s,'%self.y+'%s'%self.z
    def __add__(self, other):
        return node(self.x+other.x,self.y+other.y,self.z+other.z)
    def __sub__(self, other):
        return [self.x-other.x,self.y-other.y,self.z-other.z]


#一个排序队列
class PriorityQueue:

    def __init__(self):
        self.elements = []

    def empty(self):
        return len(self.elements) == 0

    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))

    def pop(self):
        return heapq.heappop(self.elements)[1]

    def __len__(self):
        return len(self.elements)

#对角线距离
def heuristic(tile1, tile2):

    return abs(tile1.x - tile2.x)*14 + abs(tile1.y - tile2.y)*14 + abs(tile1.z - tile2.z)*10

# 重建路径
def reconstruct_path(came_from, start, end):

    current = end
    path = [current]
    while current != start:
        current = came_from[current]
        path.append(current)
    # path.append(start)  # optional
    path.reverse()      # optional
    return path[1:]

# 在地图内
def isinmap(a,b,c,node,map,h_low,h_high):
    if node.z+c>=h_low and node.z+c<=h_high and node.x+a>=0 and node.x+a<map.shape[0] and node.y+b>=0 and node.y+b<map.shape[1]:
        if map[node.x+a][node.y+b][node.z+c]!=1:
            return True
    return False

# 找出能到达的邻域
def neighbour(n,map,h_low,h_high):
    neighbours=[]
    dirtions=[[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[1,1,0],[-1,1,0],[1,-1,0],[-1,-1,0],[0,0,1],[0,0,-1]]
    if n.z<h_low:
        for i in dirtions[-2:]:
            a, b, c = i
            if isinmap(a, b, c, n, map, 0, h_high):
                neighbours.append(node(n.x + a, n.y + b, n.z + c))
        return neighbours
    else:
        for i in dirtions:
            a,b,c=i
            if isinmap(a,b,c,n,map,0,h_high):
                neighbours.append(node(n.x+a,n.y+b,n.z+c))
        return neighbours

def a_star(start, end, map,h_low,h_high):

    frontier = PriorityQueue()
    frontier.put(start, 0)
    came_from = {start: None}
    cost_so_far = {start: 0}
    has_been_next = []
    success = False

    while not frontier.empty():
        current = frontier.pop()
        # current.visit()
        # print("next:",current.x,current.y,current.z)

        if current.x == end.x and current.y==end.y and current.z==end.z:
            # print("A* Pathfinder, successful.")
            success = True
            break

        for next_tile in neighbour(current,map,h_low,h_high):
            # print("neighbours:",next_tile.x,next_tile.y,next_tile.z)
            if next_tile not in has_been_next:
                has_been_next.append(next_tile)

            new_cost = cost_so_far[current] + 10
            if next_tile not in cost_so_far or new_cost < cost_so_far[next_tile]:
                cost_so_far[next_tile] = new_cost
                priority = new_cost + heuristic(end, next_tile)
                frontier.put(next_tile, priority)
                came_from[next_tile] = current

    return reconstruct_path(came_from, start, end)


if __name__ == '__main__':
    import numpy as np
    import time
    startt=time.clock()
    map=np.array([0]*1000000).reshape(100,100,100)
    # for i in range(0,10):
    #     for j in range(0,10):
    #         map[i][j][0]=1
    #         map[i][j][1] = 1
    # map[0][0][0]=0
    # map[0][0][1]=0
    # map[9][9][0] = 0
    # map[9][9][1] = 0
    start=node(1,1,0)
    end=node(1,1,10)
    paths=a_star(start,end,map,33,89)
    # for i in paths:
    #     print(i)
    endt=time.clock()
    print('Running time: %s Seconds' % (endt - startt))