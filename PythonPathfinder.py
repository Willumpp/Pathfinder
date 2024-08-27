import pygame, math, numpy, random, ast

#A* path finding algorithm
#Hope to only stick to integers as it should be faster to process

pygame.init()

SCREEN_SIZE = (1280, 932)

win = pygame.display.set_mode(SCREEN_SIZE)
pix_surface = pygame.Surface(SCREEN_SIZE)
pygame.display.set_caption("First window")

run = True #Main loop

RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
BLACK = (0,0,0)
WHITE = (255,255,255)
CYAN = (0, 255, 255)

def pythag(a, b):
    return math.sqrt(a**2 + b**2)

class SpecialNodes:
    def __init__(self):
        self.Floor0 = pygame.image.load("first.jpeg")
        self.Floor1 = pygame.image.load("second.jpeg")
        self.END_NODE = ""
        self.START_NODE = ""
        self.save_file = "GroundFloor.txt"

        self.floor_n = 0
        self.floor = self.Floor0

    #Save all nodes to external text file
    #   states are stored in the file for recall later
    def save_states(self):
        #Loop through every node, saving there state and logging them
        saved = []

        for x_node in nodes:
            y_nodes = []
            for y_node in x_node:
                y_nodes.append(y_node.state)

            saved.append(y_nodes)

        f = open(self.save_file, "w")
        f.write(str(saved))
        f.close()

    def set_screen(self, floor_n, is_saved=False):

        #Change file and floor selection
        if floor_n == 0:
            self.floor = self.Floor0
            self.save_file = "GroundFloor.txt"
        elif floor_n == 1:
            self.floor = self.Floor1
            self.save_file = "Floor1.txt"

        self.floor.set_alpha(127.5)

        #This gets the saved matrix of states
        #   they get set at the beginning of execution
        f = open(self.save_file, "r")
        saved = ast.literal_eval(f.read())
        f.close()

        nodes.clear()

        #Follow the saved matrix of nodes and set respective state
        if is_saved == True: 
            for x in range(0, SCREEN_SIZE[0], pixel_size):
                y_nodes = []

                #Get row of nodes
                for y in range(0, SCREEN_SIZE[1], pixel_size):
                    y_nodes.append(Node((x, y), saved[x//pixel_size][y//pixel_size]))

                nodes.append(y_nodes) #Add to the matrix
        #Set every node to a wall
        else: 
            for x in range(0, SCREEN_SIZE[0], pixel_size):
                y_nodes = []

                #Get row of nodes
                for y in range(0, SCREEN_SIZE[1], pixel_size):
                    y_nodes.append(Node((x, y), state=3))

                nodes.append(y_nodes) #Add to the matrix

class Node(SpecialNodes):
    def __init__(self, pos, state=2):
        self.x = pos[0]
        self.y = pos[1]

        self.g_cost = 0 #Distance from start (in steps)
        self.h_cost = 0 #Displacement from end
        self.f_cost = 0 #h + g

        
        #Each node should require a state
        #   this state should represent whether it is "OPEN" , "CLOSED" , "WALL" , "INACTIVE"
        #   CLOSED = 0
        #   OPEN = 1
        #   INACTIVE = 2
        #   WALL = 3
        #   START = 10
        #   END = 11
        #   EVAL = 12

        self.col = WHITE
        self.rect = pygame.Rect(self.x, self.y, pixel_size, pixel_size)

        self.set_state(state)

    def set_state(self, state):
        self.state = state

        if state == 0:
            self.col = RED
        elif state == 1:
            self.col = GREEN
        elif state == 2:
            self.col = WHITE
        elif state == 3:
            self.col = BLACK
        elif state == 10 or state == 11:
            self.col = BLUE
        elif state == 12:
            self.col = CYAN

        self.draw()

    def get_vals(self):
        print("******")
        print(f"G cost:{self.g_cost}   H cost:{self.h_cost}\n   F cost:{self.f_cost}")
        print("F cost:", self.f_cost)
        print("G cost:", self.g_cost)
        print("H cost:", self.h_cost)

    def calc_vals(self, parent_node, end_node):
        self.parent = parent_node

        self.g_cost = parent_node.g_cost + int(pythag(self.x - self.parent.x, self.y - self.parent.y))
        self.h_cost = int(pythag(self.x - end_node.x, self.y - end_node.y))
        self.f_cost = self.g_cost + self.h_cost

    def draw(self):
        pygame.draw.rect(pix_surface, self.col, self.rect)

    def get_neighbours(self):
        neighbours = [
            nodes[(self.x - pixel_size)//pixel_size][(self.y - pixel_size)//pixel_size], nodes[(self.x)//pixel_size][(self.y - pixel_size)//pixel_size], nodes[(self.x + pixel_size)//pixel_size][(self.y - pixel_size)//pixel_size],
            nodes[(self.x - pixel_size)//pixel_size][(self.y)//pixel_size],                                            nodes[(self.x + pixel_size)//pixel_size][(self.y)//pixel_size],
            nodes[(self.x - pixel_size)//pixel_size][(self.y + pixel_size)//pixel_size], nodes[(self.x)//pixel_size][(self.y + pixel_size)//pixel_size], nodes[(self.x + pixel_size)//pixel_size][(self.y + pixel_size)//pixel_size],
        ]

        return neighbours

    def retrace(self):
        self.parent.set_state(12)
        if self.parent != self:
            self.parent.retrace()


def f_lowest(): #Finds lowest f cost in open nodes
    f_costs = [node.f_cost for node in n_open]
    f_costs.sort()
    
    lowests = [node for node in n_open if node.f_cost == f_costs[0]]
    return random.choice(lowests)

#The actual A* pathfinding algorithm
def next_step():
    current_node = f_lowest() #find node in open with lowest f cost

    #remove current from open and add to closed
    n_open.remove(current_node)
    n_closed.append(current_node)

    if current_node.state == 11:
        current_node.retrace()
        return False
    else:
        current_node.set_state(0)

    #get neighbours
    neighbours = current_node.get_neighbours()

    #update neighbours
    for neighbour in neighbours:
        if neighbour.state == 3 or neighbour in n_closed:
            continue
        
        #If path of neighbour is shorter or neighbour isnt already open:
        if neighbour not in n_open or neighbour.f_cost < current_node.f_cost:
            neighbour.calc_vals(current_node, sn.END_NODE) #Gen new vals
            #neighbour.parent = current_node

            #add to open if not already in and change not the end
            if neighbour not in n_open:
                n_open.append(neighbour)
            
                if neighbour.state != 11:
                    neighbour.set_state(1)
    return True


pixel_size = 5
nodes = [] #This should be a matrix of nodes [x][y]

def gen_circle(origin, state, radius=10):
    a = origin[0]
    b = origin[1]

    nodes[a//pixel_size][b//pixel_size].set_state(state)

    points = []
    points.append([a, b+radius]) #First point

    #Flips diagonally
    def y_x_flip():
        for point in points.copy():
            x = point[1] - b + a
            y = point[0] + b - a
            points.append([x,y])

    #Flips along the y-axis
    #   uses "working" equation
    def x_flip():
        for point in points.copy():
            y = 2*b - point[1]
            points.append([point[0], y]) 
    
    #Flips along x-axis
    def y_flip():
        for point in points.copy():
            x = 2*a - point[0]
            points.append([x, point[1]])

        

    #Gen octant
    #while points[-1][0] < points[-1][1]:
    #while points[-1][0] < a + (radius):
    while (points[-1][1] - b) / ((points[-1][0] - a)+1) >= 1:
        xj = (points[-1][0]+pixel_size) - a

        # print(xj)

        #Uses pythagoras to find the distance to the circumference of the mathmatical circle
        #   start by finding the distance to origin:
        #       x**2 + y**2
        #   then subtract radius to find dist to circumference
        #   abs() so we can square root at the end
        #   square root to find the distance (error)
        r_error = xj**2 + (points[-1][1] - b)**2 - radius**2 #Red dist to circ
        b_error = xj**2 + ((points[-1][1]-pixel_size) - b)**2 - radius**2 #Black dist to circ

        r_error = math.sqrt(abs(r_error))
        b_error = math.sqrt(abs(b_error))

        #If the outside is closer to circumference, place pixel
        #   otherwise place it outside-down
        if r_error <= b_error:
            points.append([(points[-1][0]+pixel_size), (points[-1][1])])
        else:
            points.append([(points[-1][0]+pixel_size), (points[-1][1]-pixel_size)])

    y_x_flip()
    x_flip()
    y_flip()

    for point in points:
        nodes[point[0]//pixel_size][point[1]//pixel_size].set_state(state)



    #Will do the NBE octant
    #   we need to find the distance from origin to potential point A
    # point_a = 

n_open = [] #open nodes
n_closed = [] #closed nodes

place = False
first_click = []

selected = 2
#   CLOSED = 0
#   OPEN = 1
#   INACTIVE = 2
#   WALL = 3
#   START = 10
#   END = 11
#   EVAL = 12
selections = [0,1,2,3]
sel_names = {
    "0":"Closed",
    "1":"Open",
    "2":"Inactive",
    "3":"Wall",
}
sn = SpecialNodes()

rep = False #repeat next steps

radius = 5

sn.set_screen(0, is_saved=True)

#KEYS:
#   1 = prev state selection
#   2 = next state selection
#   + = increaes draw radius
#   - = decreas draw radius
#   3 = display f,g,h values
#   right key = next step of pathfind
#   left key = complete path
#   up key = next floor
#   down key = prev floor
#   shift = snap to y
#   ctrl = snap to x
#   s = save
#   r = reset
#   q, e = start, end

while run:
    #pygame.time.delay(1//60)
    win.fill((0, 0, 0))
    
    #Events like in godot
    #   more or less and event listener
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            first_click = pygame.mouse.get_pos()
            place = True

        if event.type == pygame.MOUSEBUTTONUP:
            place = False

        if event.type == pygame.KEYDOWN:
            #Choose which state of node to draw
            #min,max to clamp with array and not crash
            if event.key == pygame.K_1:
                selected = max(selected-1, 0)
            elif event.key == pygame.K_2:
                selected = min(selected+1, len(selections)-1)

            #display node values
            elif event.key == pygame.K_3:
                pos = pygame.mouse.get_pos()
                nodes[pos[0]//pixel_size][pos[1]//pixel_size].get_vals()

            #Increase/decrease radius
            if event.key == pygame.K_EQUALS:
                radius += 5
            elif event.key == pygame.K_MINUS:
                radius -= 5


            #Increment step
            if event.key == pygame.K_RIGHT:
                rep = False
                next_step()
            elif event.key == pygame.K_LEFT:
                rep = True


            #Change floors
            if event.key == pygame.K_UP:
                sn.floor_n += 1
                sn.set_screen(sn.floor_n, is_saved=True)
            elif event.key == pygame.K_DOWN:
                sn.floor_n -= 1
                sn.set_screen(sn.floor_n, is_saved=True)

            #Save/reset
            if event.key == pygame.K_s:
                sn.save_states()

            elif event.key == pygame.K_r:
                sn.set_screen(sn.floor_n, is_saved=False)

            #Set start/end
            if event.key == pygame.K_e:
                pos = pygame.mouse.get_pos()
                sn.END_NODE = nodes[pos[0]//pixel_size][pos[1]//pixel_size]
                sn.END_NODE.set_state(11)
            elif event.key == pygame.K_q:
                pos = pygame.mouse.get_pos()
                sn.START_NODE = nodes[pos[0]//pixel_size][pos[1]//pixel_size]
                n_open.append(sn.START_NODE)
                sn.START_NODE.set_state(10)
                sn.START_NODE.calc_vals(sn.START_NODE, sn.END_NODE)


        if event.type == pygame.QUIT: #If x is pressed...
            run = False

            
    keys=pygame.key.get_pressed()

    #Place pixels
    if place == True:
        pos = list(pygame.mouse.get_pos())

        #straight line drawing possibility
        if keys[pygame.K_LSHIFT]:
            pos[0] = first_click[0]
        if keys[pygame.K_LCTRL]:
            pos[1] = first_click[1]

        gen_circle([pos[0], pos[1]], selections[selected],radius=radius) #paint brush
        nodes[pos[0]//pixel_size][pos[1]//pixel_size].set_state(selections[selected]) #Drawn in set_state




    #repeat next steps if chosen
    if rep == True:
        while next_step():
            pass
        rep = False



    win.blit(pix_surface, (0,0)) #Apply every pixel
    win.blit(sn.floor, (0,0)) #Transparent surface

    pygame.display.update()

pygame.quit()