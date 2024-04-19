from RPLCD.i2c import CharLCD
import time, threading
import sys
import os

cwd = os.getcwd()
sys.path.append(os.path.dirname(cwd))
from games.snake import Snake
from drivers.keyboard import Keyboard
from communications.db import Database

class MenuItem:
    def __init__(self, name, action=None, update=None, once=None):
        self.name = name
        self.count = 0
        self.parent = None
        self.children = []
        self.setAction(action)
        self.setUpdate(update)
        self.setOnce(once)

    def __add__(self, child):
        if not isinstance(child, MenuItem):
            raise TypeError("Child must be a MenuItem.")
        child.parent = self
        self.children.append(child)

    def __repr__(self):
        return f"debug: name={self.name}\n"

    def getNthChild(self, n):
        return (
            None
            if not self.hasChildren() or n >= len(self.children)
            else self.children[n]
        )

    def hasAction(self):
        return self.action is not None

    def hasChildren(self):
        return len(self.children) > 0

    def executeAction(self):
        if self.hasAction():
            self.action()

    def __iter__(self):
        return iter(self.children)

    def _checkCallable(func):
        def wrapper(self, arg):
            if arg is not None and not callable(arg):
                raise ValueError(
                    f"The provided argument for {func.__name__[3:]} must be callable."
                )
            return func(self, arg)

        return wrapper

    @_checkCallable
    def setAction(self, action):
        self.action = action

    @_checkCallable
    def setUpdate(self, update):
        self.update = update

    @_checkCallable
    def setOnce(self, once):
        self.once = once


class Display:
    def __init__(self, cols, rows, i2cAddress, rootMenu):
        self.lcd = CharLCD(
            "PCF8574", i2cAddress, cols=cols, rows=rows, backlight_enabled=True
        )
        self.cols = cols - 1
        self.rows = rows - 1
        self.pos = 0
        self.navPos = 0
        self.inNav = False
        self.rootMenu = rootMenu
        self.currentMenu = rootMenu
        self.updateActive = False
        self.scheduler_thread = threading.Thread(target=self.run_scheduler, daemon=True)
        self.lock = threading.Lock()
        self.scheduler_thread.start()

        self.registerCustomChars()

        self.drawMenu()

    def registerCustomChars(self):
        chars = (
            [  # cursor, heart, home, back, home(selected), back (selected), expandArrow
                (
                    0b00001,
                    0b00001,
                    0b00001,
                    0b00001,
                    0b11111,
                    0b11111,
                    0b00001,
                    0b00001,
                ),
                (
                    0b00000,
                    0b01010,
                    0b11111,
                    0b11111,
                    0b01110,
                    0b00100,
                    0b00000,
                    0b00000,
                ),
                (
                    0b00100,
                    0b01110,
                    0b11111,
                    0b11011,
                    0b11011,
                    0b00000,
                    0b00000,
                    0b00000,
                ),
                (
                    0b00001,
                    0b00101,
                    0b01101,
                    0b11111,
                    0b01100,
                    0b00100,
                    0b00000,
                    0b00000,
                ),
                (
                    0b00100,
                    0b01110,
                    0b11111,
                    0b11011,
                    0b11011,
                    0b00000,
                    0b11111,
                    0b11111,
                ),
                (
                    0b00001,
                    0b00101,
                    0b01101,
                    0b11111,
                    0b01100,
                    0b00100,
                    0b11111,
                    0b11111,
                ),
                (
                    0b00000,
                    0b00000,
                    0b00000,
                    0b00000,
                    0b10001,
                    0b11011,
                    0b01110,
                    0b00100,
                ),
            ]
        )

        for i, ch in enumerate(chars):
            self.lcd.create_char(i,ch)

    def run_scheduler(self):
        def pad_item(header, item):
            return item + (" " * (20 - len(item)+len(header)))
        while True:
            for row, child in enumerate(self.currentMenu):
                if child.update is not None:
                    content = child.update()
                    header = child.name
                    if len(header) + len(content) > 20:
                        print("info: skipping update. content is too long.")
                        continue
                    self.updateItem(row, content, col_pos=len(header))
            time.sleep(1)

    def updateItem(self, row, content, col_pos=0):
        with self.lock:
            prefix = "\x00" if self.pos == row and not self.inNav else " "
            line = f"{prefix}{content[:self.cols-1]}"

            self.lcd.cursor_pos = (row, col_pos)
            self.lcd.write_string(line)

    def drawNavigation(self):
        icons = ["\x02", "\x03"]
        if self.inNav:
            if self.navPos == 0:
                icons[0] = "\x04"
            else:
                icons[1] = "\x05"

        self.lcd.cursor_pos = (0, self.cols)  # home button
        self.lcd.write_string(icons[0])
        self.lcd.cursor_pos = (self.rows, self.cols)  # draw back button
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

        self.drawNavigation()

    def cleanup(self, clear):
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
