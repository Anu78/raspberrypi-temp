from RPLCD.i2c import CharLCD
import time
import threading

class MenuItem:
    def __init__(self, name, action=None, update=None, parent=None, once=None):
        self.name = name
        self.action = action
        self.update = update
        self.once = once
        self.count = 0
        self.parent = parent
        self.children = []
    def addChildren(self, children): 
        for child in children: 
            child.parent = self
        self.children.extend(children)
    def __str__(self): 
        return f"debug: name={self.name}\n"
    def getNthChild(self, n): 
        return None if not self.hasChildren() or n > len(self.children) else self.children[n]
    def hasAction(self): 
        return False if self.action is None else True
    def hasChildren(self): 
        return False if len(self.children) == 0 else True
    def executeAction(self):
        """
        will include threading and async execution soon
        """
        if self.action is not None:
            self.action()

    # iterator things
    def __iter__(self): 
        return self
    def __next__(self):
        if self.count < len(self.children):
            currentChild = self.children[self.count]
            self.count += 1  
            return currentChild 
        else:
            self.count = 0  
            raise StopIteration

    def _checkCallable(func):
        def wrapper(self, arg): 
            if not callable(arg):
                raise ValueError(f"{func.__name__} argument must be callable.")
            return func(self, arg)
        return wrapper

    @_checkCallable
    def addAction(self, action):
        self.action = action 

    @_checkCallable
    def addOnce(self, once):
        self.once = once

    @_checkCallable
    def addUpdate(self, update): 
        self.update = update  

class Display:
    def __init__(self, cols, rows, i2cAddress, rootMenu):
        self.lcd = CharLCD(
            "PCF8574", i2cAddress, cols=cols, rows=rows, backlight_enabled=True
        )
        self.cols = cols - 1
        self.rows = rows - 1
        self.pos = 0  # row number
        self.navPos = 0
        self.inNav = False
        self.rootMenu = rootMenu
        self.currentMenu = rootMenu
        self.updateActive = False

        # create custom chars
        self.registerCustomChars()

        # draw the root menu and navigation
        self.drawMenu()

    def registerCustomChars(self):
        chars = [  # cursor, heart, home, back, home(selected), back (selected), expandArrow 
            (0b00001, 0b00001, 0b00001, 0b00001, 0b11111, 0b11111, 0b00001, 0b00001),
            (0b00000, 0b01010, 0b11111, 0b11111, 0b01110, 0b00100, 0b00000, 0b00000),
            (0b00100, 0b01110, 0b11111, 0b11011, 0b11011, 0b00000, 0b00000, 0b00000),
            (0b00001, 0b00101, 0b01101, 0b11111, 0b01100, 0b00100, 0b00000, 0b00000),
            (0b00100, 0b01110, 0b11111, 0b11011, 0b11011, 0b00000, 0b11111, 0b11111),
            (0b00001, 0b00101, 0b01101, 0b11111, 0b01100, 0b00100, 0b11111, 0b11111),
            (0b00000, 0b00000, 0b00000, 0b00000, 0b10001, 0b11011, 0b01110, 0b00100)
        ]

        for i in range(len(chars)):
            self.lcd.create_char(i, chars[i])

    def startUpdating(self): 
        self.updateActive = True
        self.updateThread = threading.Thread(target=self.updateContent)
        self.updateThread.start()
    def stopUpdating(self):
        self.updateActive = False
        if self.updateThread:
            self.updateThread.join()

    def updateContent(self):
        """
        will reduce display re-draw soon by only changing updated text instead of whole menu. 
        """
        while self.updateActive:
            if self.currentMenu.hasChildren():
                for i, child in enumerate(self.currentMenu.children):
                    if child.update:
                        newContent = child.update()
                        if newContent:
                            newPos = (i, len(child.name) + 1)
                            self.lcd.cursor_pos = newPos 
                            self.lcd.write_string(newContent[:self.cols+1])
            time.sleep(2.5)

    def drawNavigation(self):
        icons = ["\x02", "\x03"]
        if self.inNav:
            if self.navPos == 0:
                icons[0] = "\x04"
            else: 
                icons[1] = "\x05" 

        self.lcd.cursor_pos = (0, self.cols) # home button 
        self.lcd.write_string(icons[0])
        self.lcd.cursor_pos = (self.rows, self.cols) # draw back button 
        self.lcd.write_string(icons[1])

    def drawMenu(self):
        self.lcd.clear()

        for row, child in enumerate(self.currentMenu):
            prefix = "\x00" if self.pos == row and not self.inNav else " "

            line = f"{prefix}{child.name[:self.cols-1]}"
            if child.once is not None: 
                output = child.once()
                if len(line) + len(output) > self.cols + 1: 
                    print("info: not displaying content due to length.")
                else: 
                    line += output
            if child.hasChildren(): 
                line += "\x06"
            
            self.lcd.cursor_pos = (row, 0)
            self.lcd.write_string(line)

        self.startUpdating()
        self.drawNavigation()

    def cleanup(self, clear):
        self.stopUpdating()
        self.lcd.close(clear=clear)

    def move(self, new):
        if self.inNav:
            self.navPos = (self.navPos + new) % 2
            self.drawNavigation()
        else:
            self.lcd.cursor_pos = (self.pos, 0)
            self.lcd.write_string(" ")
            self.pos = (self.pos + new) % (self.rows + 1)

            self.lcd.cursor_pos = (self.pos, 0)
            self.lcd.write_string("\x00")
    def select(self):
        currentChild = self.currentMenu.getNthChild(self.pos)
        if self.inNav:
            if self.navPos == 0:
                self.currentMenu = self.rootMenu
                self.outNav()
                self.drawMenu()
            else:
                self.back()
        elif currentChild.hasAction(): 
            currentChild.executeAction()
        else:
            self.forward()
    def forward(self):
        current = self.currentMenu.getNthChild(self.pos)
        if current is not None: 
            if current.hasChildren():
                self.currentMenu = current 
                self.pos = 0
                self.stopUpdating()
                self.drawMenu()
    def back(self):
        if self.currentMenu.parent is None:
            return
        else: 
            self.currentMenu = self.currentMenu.parent
        self.stopUpdating()
        self.drawMenu()

    def intoNav(self):
        self.inNav = True
        self.drawMenu()
    def outNav(self):
        self.inNav = False
        self.drawMenu()
