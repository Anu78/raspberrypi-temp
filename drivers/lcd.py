from RPLCD.i2c import CharLCD

class MenuItem:
  def __init__(self, name, action=None, parent=None):
    self.name = name 
    self.action = action
    self.parent = parent
    self.items = []

  def addItem(self, item): 
    self.items.append(item) 

  def execute(self): 
    if self.action:
      self.action()

class Display:
  def __init__(self, cols, rows, i2cAddress, menuItems): 
    self.lcd = CharLCD('PCF8574', 0x27, cols=cols, rows=rows, backlight_enabled=True)
    self.menuItems = menuItems # const list of menu items
    self.cols = cols
    self.rows = rows
    self.menuPosition = (0, 0) # max of two nested menus (main, sub)  

    # create menu item selected char and heart 
    self.registerCustomChars()

  def registerCustomChars(self): 
    smiley = (
        0b00000,
        0b00000,
        0b01010,
        0b00000,
        0b00100,
        0b10001,
        0b01110,
        0b00000
        )
    heart = (
        0b00000,
        0b01010,
        0b11111,
        0b11111,
        0b01110,
        0b00100,
        0b00000,
        0b00000
        )
    self.lcd.create_char(0, smiley) 
    self.lcd.create_char(1, heart)

  def getIPAddress(self): 
    from subprocess import check_output
    ips = check_output(['hostname', '--all-ip-addresses'])
    return ips.decode('utf-8').strip()

  def drawOneLine(self, text): 
    self.lcd.write_string(text)

  def drawMenu(self, selectedItem):
    self.lcd.clear() 

    for i in range(min(self.rows, len(self.menuItems))): 
      if i == self.menuPosition: 
        prefix = "\x00 "
      else: 
        prefix = "  "

      text = prefix + self.menuItems[i] + "\n\r"
      self.lcd.write_string(text) 

      self.lcd.close(False)

  def close(self, clear):
    self.lcd.close(clear=clear)

  def redrawSelection(self, newPosition):
    self.lcd.cursor_pos = (self.menuPosition[0], 0)
    self.write_string(" ") 
    self.lcd.cursor_pos = (newPosition, 0) 
    self.write_string("\x00 ") 


  def moveUp(self):
    self.menuPosition = (self.menuPosition + 1) % self.rows # wrap around 
    self.drawMenu()
    
  def moveDown(self):
    self.menuPosition = (self.menuPosition - 1) % self.rows # wrap around 
    self.drawMenu()


if __name__ == "__main__":
  menu = ["hello", "world"] 
  lcd = Display(cols=20, rows=4, i2cAddress=0x27, menuItems=menu)

  lcd.drawMenu(1)

  print(lcd.getIPAddress())

  lcd.close(clear=False)
