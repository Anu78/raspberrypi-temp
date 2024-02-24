from RPLCD.i2c import CharLCD

class MenuItem:
    def __init__(self, name, action=None, update=None, parent=None, once=None):
        self.name = name
        self.action = action
        self.update = update
        self.parent = parent
        self.children = []
    def addChildren(self, children): 
        for child in children: 
            child.parent = self
        self.children.extend(children)
    def __str__(self): 
        return f"debug: name={self.name}\n"
    def getChildren(self):
        return None if len(self.children) == 0 else self.children
    def getNthChild(self, n): 
        return None if not self.hasChildren() or n > len(self.children) else self.children[n]
    def hasAction(self): 
        return False if self.action is None else True
    def hasChildren(self): 
        return False if len(self.children) == 0 else True
    def getSubItems(self): 
        if self.hasChildren():
            return [child.name for child in self.children]
        else:
            return None

    def _checkCallable(func):
        def wrapper(self, arg): 
            if not callable(arg):
                raise ValueError(f"{func.__name__} argument must be callable.")
            return func(self, arc)
        return wrapper

    @_checkCallable
    def addAction(self, action):
        self.action = action 

    @_checkCallable
    def addOnce(self, once):
        self.once = once

    @_checkCallable
    def addUpdate(self, update): 
        self.update = update @_ 
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

        # create custom chars
        self.registerCustomChars()

        # draw the root menu and navigation
        self.drawMenu()

    def registerCustomChars(self):
        chars = [  # smiley, heart, home, back, home(selected), back (selected) 
            (0b00000, 0b00000, 0b01010, 0b00000, 0b00100, 0b10001, 0b01110, 0b00000),
            (0b00000, 0b01010, 0b11111, 0b11111, 0b01110, 0b00100, 0b00000, 0b00000),
            (0b00100, 0b01110, 0b11111, 0b11011, 0b11011, 0b00000, 0b00000, 0b00000),
            (0b00001, 0b00101, 0b01101, 0b11111, 0b01100, 0b00100, 0b00000, 0b00000),
            (0b00100, 0b01110, 0b11111, 0b11011, 0b11011, 0b00000, 0b11111, 0b11111),
            (0b00001, 0b00101, 0b01101, 0b11111, 0b01100, 0b00100, 0b11111, 0b11111),
        ]

        for i in range(len(chars)):
            self.lcd.create_char(i, chars[i])

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
        toRender = self.currentMenu.getSubItems()
        if toRender is None:
            return

        self.lcd.clear()
        for row, item in enumerate(toRender): 
            prefix = "\x00" if self.pos == row and not self.inNav else " "

            line = f"{prefix} {item[:self.cols-1]}"
            self.lcd.cursor_pos = (row, 0)
            self.lcd.write_string(line)
        
        self.drawNavigation()

    def close(self, clear):
        self.lcd.close(clear=clear)

    def move(self, new):
        if self.inNav:
            self.navPos = (self.navPos + new) % 2
            self.drawNavigation()
        else:
            # redraw cursor
            self.lcd.cursor_pos = (self.pos, 0)
            self.lcd.write_string(" ")
            self.pos = (self.pos + new) % (self.rows + 1)

            self.lcd.cursor_pos = (self.pos, 0)
            self.lcd.write_string("\x00")
    def select(self):
        if self.inNav:
            if self.navPos == 0:
                self.currentMenu = self.rootMenu
                self.outNav()
                self.drawMenu()
            else:
                self.back()
        else:
            self.forward()
    def forward(self):
        current = self.currentMenu.getNthChild(self.pos)
        if current is not None: 
            if current.hasChildren():
                self.currentMenu = current 
                self.pos = 0
                self.drawMenu()
    def back(self):
        if self.currentMenu.parent is None:
            return
        else: 
            self.currentMenu = self.currentMenu.parent
        self.drawMenu()

    def intoNav(self):
        self.inNav = True
        self.drawMenu()
    def outNav(self):
        self.inNav = False
        self.drawMenu()


def fancyInterpreter(lcd):
    while True:
        s = input(">> ")

        if s == "bye" or s == "exit":
            print("bye!")
            break
        elif s == "u":
            lcd.move(-1)
        elif s == "h":
            print("h for help | u d l r to m | sel to select | back for back")
        elif s == "d":
            lcd.move(1)
        elif s == "l":
            lcd.outNav()
        elif s == "r":
            lcd.intoNav()
        elif s == "sel":
            lcd.select()
        elif s == "back":
            lcd.back()
        else:
            print("command not recognized")

def getIPAddress(self):
    from subprocess import check_output

    ips = check_output(["hostname", "--all-ip-addresses"])

    parsed = ips.decode("utf-8").strip()

    # sometimes this includes the mac address, so filtering:
    return parsed[parsed.find(" ") :]

def buildMenu(): 
    rootMenu = MenuItem("main menu")
    motorControl = MenuItem("motor control")
    motorCalibrate = MenuItem("calibrate")
    motorCalibrate.addChildren([MenuItem("menu test")])

    motorControl.addChildren([MenuItem("motor out"), MenuItem("motor in"), MenuItem("motor home"), motorCalibrate])

    preheat = MenuItem("preheat")
    about = MenuItem("about")
    connection = MenuItem("connection")
    connection.addChildren([MenuItem("ip: "), MenuItem("online?")])

    rootMenu.addChildren([motorControl, preheat, about, connection])

    return rootMenu

if __name__ == "__main__":
    menu = buildMenu()
    lcd = Display(cols=20, rows=4, i2cAddress=0x27, rootMenu=menu)

    fancyInterpreter(lcd)  # temp interpreter for navigating menu

    lcd.close(clear=False)
