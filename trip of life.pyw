import pyglet
from pyglet.window import key
from pyglet.gl import *
from app import App
from Tkinter import *
from tkFileDialog import askopenfilename, asksaveasfilename

size = 8
half_size = size/2
extension = {"defaultextension":"life", "filetypes":[('life','.life')]}


class CreateDialog:
    def __init__(self, parent, game):
        top = self.top = Toplevel(parent)
        self.game = game

        Label(top, text="Columns:").pack()
        self.c = Entry(top)
        self.c.pack(padx=5)

        Label(top, text="Rows:").pack()
        self.r = Entry(top)
        self.r.pack(padx=5)

        b = Button(top, text="Create", command=self.ok)
        b.pack(pady=5)

        top.bind('<Return>', self.enter)

    def enter(self, event):
        self.ok()

    def ok(self):
        self.game.create(int(self.c.get()),int(self.r.get()))
        self.top.destroy()


class Cell(object):
    def __init__(self, game, x, y):
        self.world = game.world
        self.batch = game.app.batch
        self.group = game.app.sprite_group
        self.x = x
        self.y = y
        self.state = False
        self.neighbours = 0
        self.vertex_list = self.dead_vertex_list()

    def set_vertex_list(self):
        self.vertex_list.delete()
        if self.state:
            self.vertex_list = self.alive_vertex_list()
            
        else:
            self.vertex_list = self.dead_vertex_list()

    def dead_vertex_list(self):
        x = self.x * size
        y = self.y * size
        vertices = (x+half_size, y,
                    x, y+half_size,
                    x, y+half_size,
                    x+half_size, y+size,
                    x+half_size, y+size,
                    x+size, y+half_size,
                    x+size, y+half_size,
                    x+half_size, y)
        return self.batch.add(8, GL_LINES, self.group, ('v2i', vertices), ('c3B', self.color(8))) 


    def alive_vertex_list(self):
        x = self.x * size
        y = self.y * size
        vertices = (x, y,
                    x, y+size,
                    x+size, y+size,
                    x+size, y)
        return self.batch.add(4, GL_QUADS, self.group, ('v2i', vertices), ('c3B', self.color(4)))

    def color(self, count):
        red = 0
        green = 0
        blue = 0
        if self.state:
            if self.neighbours > 3:
                red = 255
            elif self.neighbours < 2:
                blue = 255
            else:
                green = 255
        else:
            if self.neighbours > 3:
                red = 60
            elif self.neighbours < 3:
                blue = 60
            else:
                green = 100
                
        return (red, green, blue)*count

    def set_color(self):
        self.vertex_list.colors = self.color(len(self.vertex_list.vertices)/2)

    def toggle(self):
        self.set_state(not self.state)

    def set_state(self, state):
        if state:
            self.spawn()
        else:
            self.die()

    def die(self):
        if self.state:
            self.state = False
            self.set_vertex_list()
            self.mod_neighbours(-1)

    def spawn(self):
        if not self.state:
            self.state = True
            self.set_vertex_list()
            self.mod_neighbours(1)

    def reset(self):
        self.state = False
        self.neighbours = 0
        self.set_vertex_list()
    
    def mod_neighbours(self, mod):
        for x in range(-1,2):
            for y in range(-1,2):
                if x == 0 and y == 0:
                    pass
                else:
                    try:
                        cell = self.world[(self.x+x, self.y+y)]
                        cell.neighbours += mod
                        cell.set_color()
                    except KeyError:
                        pass


class GameHandlers(object):
    def __init__(self, game):
        self.game = game
        self.game.app.window.push_handlers(self)
        
    def on_key_press(self, symbol, modifiers):
        if not modifiers & key.MOD_CTRL:
            if symbol == key.SPACE:
                self.game.toggle()
            elif symbol == key.DELETE:
                self.game.reset()
            elif symbol == key.ENTER:
                self.game.create_dialog()
            elif symbol == key.S:
                self.game.save_dialog()
            elif symbol == key.L:
                self.game.load_dialog()
            elif symbol == key.N:
                self.game.next_step()
        
    def on_mouse_press(self, x, y, button, modifiers):
        self.game.draw_press(x,y)
 
    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        self.game.draw_drag(x,y)
    

class Game(object):
    def __init__(self, app, columns, rows):
        self.app = app
        self.running = False
        self.tk = None
        self.draw_last = (-1,-1)
        self.draw_state = True
        self.handlers = GameHandlers(self)
        self.create(columns, rows)


    def next_step(self):
        if not self.running:
            self.update()

    def draw_press(self, x, y):
        if self.tk is None:
            try:
                cell = self.world[x/size,y/size]
                cell.toggle()
                self.draw_state = cell.state
            except KeyError:
                pass

            
    def draw_drag(self, x, y):
        if self.tk is None:
            try:
                now = (x/size, y/size)
                cell = self.world[now]
                if self.draw_last != now and cell.state != self.draw_state:
                    self.world[now].set_state(self.draw_state)
                    self.draw_last = now      
            except KeyError:
                pass
            

    def save_dialog(self):
        self.stop()
        Tk().withdraw()
        filename = asksaveasfilename(**extension)
        self.save(filename)


    def load_dialog(self):
        self.stop()
        Tk().withdraw()
        filename = askopenfilename(**extension)
        self.load(filename)


    def activate_caption(self, text):
        self.app.window.activate()
        self.caption(text)

        
    def caption(self, text):
        self.app.window.set_caption(text)


    def check_filename(self, name, caption):
        if name == "":
            self.activate_caption(caption)
            return False
        return True


    def open_filename(self, name, caption):
        try:
            f = open(name, 'r')
        except IOError:
            self.activate_caption(caption)
            return None
        return f

    
    def save(self, name):
        if not self.check_filename(name, "Saving failed, no filename specified!"):
            return
        
        self.caption("Saving: " + name)
        
        f = open(name, 'w')
        
        string = ""
        for x in range(self.columns):
            for y in range(self.rows):
                cell = self.world[(x,y)].state
                if cell:
                    string += "a"
                else:
                    string += "d"
            string += "\n"
            
        f.write(string)
        f.close()

        self.activate_caption("Saving done!")


    def load(self, name):
        if not self.check_filename(name, "Loading failed, no filename specified!"):
            return

        f = self.open_filename(name, "Loading failed, specified file not found!")
        if not f:
            return
        
        self.caption("Loading: " + name)
        
        lines = []
        for line in f:
            lines.append(line)
            
        columns = len(lines)
        rows = len(lines[0])-1

        self.create(columns, rows)
        
        for x in range(columns):
            for y in range(rows):
                char = lines[x][y]
                if char == "a":
                    state = True
                else:
                    state = False
                cell = self.world[(x,y)]
                cell.set_state(state)

        self.activate_caption("Loading done!")


    def reset(self):
        self.stop()
        for key in self.world:
            self.world[key].reset()

            
    def create_dialog(self):
        self.stop()
        if self.tk is None:
            self.tk = Tk()
            self.tk.title("Create...")
            self.tk.withdraw()
            self.tk.update()

            dialog = CreateDialog(self.tk, self)
            self.tk.wait_window(dialog.top)
            self.tk = None

        
    def create(self, columns, rows):
        self.app.rebatch()

        self.columns = columns
        self.rows = rows
        
        self.world = dict()
        for x in range(columns):
            for y in range(rows):
                self.world[(x,y)] = Cell(self, x, y)
        if not self.app.window.fullscreen:
            self.app.window.set_size(columns*size,rows*size)
        
        
    def toggle(self):
        if self.running:
            self.stop()
        else:
            self.start()


    def start(self):
        self.app.window.set_caption("Running...")
        self.running = True
        pyglet.clock.schedule(self._update)


    def stop(self):
        self.app.window.set_caption("Paused...")
        self.running = False
        pyglet.clock.unschedule(self._update)


    def _update(self, dt):
        self.update()

        
    def update(self):
        die = []
        spawn = []
        for key in self.world:
            cell = self.world[key]
            if cell.state:
                if cell.neighbours > 3:
                    die.append(cell)
                elif cell.neighbours < 2:
                    die.append(cell)
            else:
                if cell.neighbours == 3:
                    spawn.append(cell)

        for cell in die:
            cell.die()
        for cell in spawn:
            cell.spawn()



app = App()
game = Game(app, app.window.width/size, app.window.height/size)
app.run()
