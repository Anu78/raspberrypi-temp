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
    ret = ""
    for node in self:
      ret += f"{node.pos}->"
    return ret[:-3] 
  
  def __iter__(self):
    current = self
    while current:
      yield current
      current = current.next

class Snake: 
  def __init__(self, display, updateDelay=0.25):
    self.display = display 
    self.lcd = display.lcd
    self.updateDelay = updateDelay
    self.spawnFood()
    self.initialize()
    self.registerNewChars()
  def initialize(self):
    self.head = LinkedList(Point(10,2), direction=3)
    temp = self.head
    # add 2 starting nodes
    for i in range(1,4): 
      temp.next = LinkedList(Point(10+i, 2), direction=3)
      temp = temp.next  
  def spawnFood(self): 
    self.food_pos = Point(random.randint(0,19), random.randint(0,3))
    for node in self.head:
      if node.pos == self.head.pos:
        self.spawnFood()

  def foodEaten(self): 
    self.head.next = LinkedList(position=()) 
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
    # other cleanup
    pass
  def draw(self):
    # draw body
    for i, node in enumerate(self.head):
      self.lcd.cursor_pos = (node.pos.y, node.pos.x)
      self.lcd.write_string("\x01" if i != 0 else "\x00") 

    # draw food
    self.lcd.cursor_pos = (node.pos.y, node.pos.x)
    self.lcd.write_string("\x02")

  def drawCountdown(self):
    self.lcd.cursor_pos = (2,2)
    self.lcd.write_string("starting in 4")
    self.lcd.cursor_pos = (2, len("starting in 4")+1)
    for i in range(3, 0, -1):
      self.lcd.write_string(str(i))
      time.sleep(1)
  def start(self):
    self.drawCountdown()
    try:
      while True:
        # main game loop
        # check if head overlaps food 

        # loop through linked list of head and update positions
        for i, node in enumerate(self.head):
          pass

        # re-draw display 
        self.draw()
        # wait for vis update
        time.sleep(self.updateDelay)
        pass
    # replace with another button press
    except KeyboardInterrupt:
      self.exit()
      time.sleep(1) # wait for things to return to normal


from drivers.display import Display
display = Display()
if __name__ == "__main__":
  game = Snake(display=display)
  game.start()