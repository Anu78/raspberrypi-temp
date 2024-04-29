import time
import random

class Point:
  def __init__(self,x,y):
    self.x = x
    self.y = y
  def __eq__(self, other):
    return True if self.x == other.x and self.y == other.y else False
  def __repr__(self):
    return f"{self.x},{self.y}"

class LinkedList:
  def __init__(self, pos, direction): 
    self.pos = pos 
    self.direction = direction 
    self.next = None

  # linked list debug function
  def __repr__(self):
    return "".join([f"{node.pos}->" for node in self][:-3])
  def __iter__(self):
    current = self
    while current:
      yield current
      current = current.next

class Snake: 
  def __init__(self, display, keyboard, updateDelay=0.25):
    self.display = display 
    self.lcd = display.lcd
    self.updateDelay = updateDelay
    self.initialize()
    self.spawnFood()
    self.registerNewChars()
    self.score = 0
    self.keyboard = keyboard
    self.highscore = 0
  def initialize(self):
    self.lcd.clear()
    self.head = LinkedList(Point(10,2), direction=3)
    temp = self.head
    # add 2 starting nodes
    for i in range(1,4): 
      temp.next = LinkedList(Point(10+i, 2), direction=3)
      temp = temp.next  
    self.tail = temp
    # get current high score from params
    # self.highscore = int(self.db.get_parameters()["snake_highscore"])
  def spawnFood(self): 
    while True:
      self.food_pos = Point(random.randint(0,19), random.randint(0,3))
      if all(self.food_pos != node.pos for node in self.head):
        break
  def foodEaten(self): 
    new_segment = LinkedList(Point(self.tail.pos.x, self.tail.pos.y), direction=self.tail.direction)
    self.tail.next = new_segment
    self.tail = new_segment
    self.score += 1
    self.spawnFood()
  def registerNewChars(self):
    # register snake head and body 
    head = (
      0x00,
      0x00,
      0x00,
      0x0E,
      0x0E,
      0x0E,
      0x00,
      0x00
    )
    body = (
      0x00,
      0x00,
      0x1F,
      0x1F,
      0x1F,
      0x1F,
      0x1F,
      0x00
    )
    food = (
      0x00,
      0x04,
      0x04,
      0x0E,
      0x1F,
      0x1F,
      0x0E,
      0x04
    )
    self.lcd.create_char(0, head)
    self.lcd.create_char(1, body)
    self.lcd.create_char(2, food)
  def exit(self): 
    # re-register normal custom characters
    self.lcd.registerCustomChars()
    
    # re-draw menu just in case
    self.lcd.drawMenu()
  def draw(self):
    # draw body
    for i, node in enumerate(self.head):
      self.lcd.cursor_pos = (node.pos.y, node.pos.x)
      self.lcd.write_string("\x01" if i != 0 else "\x00") 

    # draw food
    self.lcd.cursor_pos = (self.food_pos.y, self.food_pos.x)
    self.lcd.write_string("\x02")

  def drawCountdown(self):
    self.lcd.cursor_pos = (2,2)
    self.lcd.write_string("starting in 4")
    self.lcd.cursor_pos = (2, len("starting in 4")+1)
    for i in range(3, 0, -1):
      self.lcd.write_string(str(i))
      time.sleep(1)
    self.lcd.clear()

  def move(self, direction):
    prev_pos = Point(self.head.pos.x, self.head.pos.y)

    if direction == 'u':
        self.head.pos.y -= 1
    elif direction == 'd':
        self.head.pos.y += 1
    elif direction == 'l':
        self.head.pos.x -= 1
    elif direction == 'r':
        self.head.pos.x += 1

    current_node = self.head.next
    while current_node is not None:
        temp_pos = Point(current_node.pos.x, current_node.pos.y)
        current_node.pos = prev_pos
        prev_pos = temp_pos
        current_node = current_node.next


  def change_direction(self, current_direction, new_direction):
    if current_direction == 'u' and new_direction == 'd':
        return current_direction  
    if current_direction == 'd' and new_direction == 'u':
        return current_direction
    if current_direction == 'l' and new_direction == 'r':
        return current_direction
    if current_direction == 'r' and new_direction == 'l':
        return current_direction
    return new_direction  

  def gameOver(self):
    self.lcd.clear()

    self.lcd.cursor_pos = (0,2)
    self.lcd.write_string(f"GAME OVER. len {self.score}")
    self.lcd.write_string(f"highscore: {self.highscore}")

    if self.score > self.highscore:
      self.lcd.cursor_pos = ((20-len("new high score"))//2,3)
      self.lcd.write_string(f"new high score!")

    time.sleep(3)
    self.exit()
  def start(self):
    self.lcd.clear()
    direction = 'l'
    self.drawCountdown()

    while True:
        key = self.keyboard.get_key()
        if key:
          new_direction = self.change_direction(direction, key) 
          direction = new_direction

        self.move(direction)
            
        if self.head.pos == self.food_pos:
            self.foodEaten()

        current_pos = self.head.pos
        for node in self.head.next:
            if node.pos == current_pos:
                print("you hit yourself")
                break

        if self.head.pos.x > 19 or self.head.pos.y > 4 or self.head.pos.x < 0 or self.head.pos.y < 0:
          break

        self.draw()

        time.sleep(self.updateDelay)

        self.lcd.clear()
    
    self.gameOver()