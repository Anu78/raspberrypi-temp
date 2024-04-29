from RPLCD.i2c import CharLCD
import time, threading
from games.snake import Snake
import queue 

class MenuItem:
    def __init__(self, name, action=None, update=None, once=None):
        self.name = name
        self.count = 0
        self.parent = None
        self.children = []
        self.set_action(action)
        self.set_update(update)
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
    def set_action(self, action):
        self.action = action

    @_checkCallable
    def set_update(self, update):
        self.update = update

    @_checkCallable
    def setOnce(self, once):
        self.once = once

class ToggleItem(MenuItem):
    def __init__(self, name, on_action, off_action):
        super().__init__(name)
        self.on = False  
        self.orig_name = name  
        self.name = f"{self.orig_name} (off)" 
        self.on_action = on_action if callable(on_action) else None
        self.off_action = off_action if callable(off_action) else None

    def start(self):
        if not self.on:
            self.on = True
            self.name = f"{self.orig_name} (on)"  
            if self.on_action:  
                self.on_action()

    def stop(self):
        if self.on:
            self.on = False
            self.name = f"{self.orig_name} (off)"  
            if self.off_action:  
                self.off_action()

    def toggle(self):
        if self.on:
            self.stop()  
        else:
            self.start() 

class Display:
    def __init__(self, cols, rows, i2cAddress, rootMenu, keyboard):
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
        self.update_queue_thread = threading.Thread(target=self.populate_queue, daemon=True)
        self.update_display_thread = threading.Thread(target=self.run_update, daemon=True)
        self.lock = threading.Lock()
        self.keyboard = keyboard
        self.update_queue = queue.Queue() 
        self.update_queue_thread.start()
        self.update_display_thread.start()
        self.is_updating = False

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

    def populate_queue(self):
        while True:
            for row, child in enumerate(self.currentMenu):
                if child.update is not None:
                    self.update_queue.put((row, child.name, time.time(), child.update()))
                time.sleep(1)

    def run_update(self):
        while True: 
            if not self.update_queue:
                time.sleep(1)
                continue
            row, name, rtime, update = self.update_queue.get()
            if len(name) + len(update) > 20:
                print("info: skipping update. content is too long.")
                self.update_queue.task_done()
                continue
            self.is_updating = True
            pad_amt = 20 - (len(name) + len(update))
            self.updateItem(row, update, col_pos=len(name)+1, pad=pad_amt)
            self.update_queue.task_done()
            self.is_updating = False
            time.sleep(1.5)

    def updateItem(self, row, content, col_pos=0, pad=0):
        with self.lock:
            line = f"{content[:self.cols-1]}"
            line += " " * (pad - len(line)) # clear entire line to avoid overwriting

            self.lcd.cursor_pos = (row, col_pos)
            self.lcd.write_string(line)

    def drawNavigation(self):
        if self.is_updating:
            return
        icons = ["\x02", "\x03"]
        if self.inNav:
            if self.navPos == 0:
                icons[0] = "\x04"
            else:
                icons[1] = "\x05"

        with self.lock:
            self.lcd.cursor_pos = (0, self.cols)  # home button
            self.lcd.write_string(icons[0])
            self.lcd.cursor_pos = (self.rows, self.cols)  # draw back button
            self.lcd.write_string(icons[1])

    def drawMenu(self):
        if self.is_updating:
            return
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
            with self.lock:
                self.lcd.write_string(line)

        self.drawNavigation()

    def cleanup(self, clear):
        self.lcd.close(clear=clear)

    def move(self, new):
        if self.is_updating:
            return
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
        if self.is_updating:
            return
        currentChild = self.currentMenu.getNthChild(self.pos)
        if self.inNav:
            # clear queue here?
            with self.lock:
                while self.update_queue:
                    self.update_queue.get_nowait()
            if self.navPos == 0:
                self.currentMenu = self.rootMenu
                self.outNav()
                self.drawMenu()
            else:
                self.back()
        elif hasattr(currentChild, 'toggle') and not self.is_updating: # check for toggle
            currentChild.toggle()
            self.drawMenu()
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
