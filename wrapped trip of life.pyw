import pyglet
from pyglet.window import key
from pyglet.gl import *
from app import App
from Tkinter import *
from tkFileDialog import askopenfilename, asksaveasfilename



size = 64
half_size = size/2
double_size = size*2
big_size = size*32
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
        try:
            self.game.create(int(self.c.get()),int(self.r.get()))
        except ValueError:
            self.game.activate_caption("Creating failed, invalid input!")
        self.top.destroy()



class Cell(object):
    def __init__(self, game, x, y):
        self.game = game
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
                    xx = self.x+x
                    yy = self.y+y

                    if self.game.wrapping:
                        xx, yy = self.game.wrapped(xx, yy)
                    try:
                        cell = self.world[(xx, yy)]
                        cell.neighbours += mod
                        cell.set_color()
                    except KeyError:
                        pass



class CursorHandlers(object):
    def __init__(self, game):
        self.game = game
        game.app.window.push_handlers(self)


    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        self.game.cursor.move(x, y)


    def on_mouse_motion(self, x, y, dx, dy):
        self.game.cursor.move(x, y) 



class Cursor(object):
    def __init__(self, game):
        self.handlers = CursorHandlers(game)
        self.app = game.app
        self.app.window.set_mouse_visible(False)
        x = self.app.mouse.x - self.app.mouse.x % size
        y = self.app.mouse.y - self.app.mouse.y % size
        self.last = (x, y)
        self.vertex_list = self.app.batch.add(24, GL_LINES, self.app.text_group, ('v2i', self.vertices(x, y)), ('c4B', self.color()))

    
    def color(self):
        shadow = (0,0,0,200)*8
        inside = (255,255,255,200)*8
        outside = (255,255,255,100,
                   255,255,255,0)*4

        return shadow+inside+outside 

    
    def vertices(self, x, y):
        shadow = (x, y,
                  x+size, y,
                  x+size, y,
                  x+size, y+size,
                  x+size, y+size,
                  x, y+size,
                  x, y+size,
                  x, y)
            
        inside = (x-1, y-1,
                  x+size+1, y-1,
                  x+size+1, y-1,
                  x+size+1, y+size+1,
                  x+size+1, y+size+1,
                  x-1, y+size+1,
                  x-1, y+size+1,
                  x-1, y-1)

        outside = (x, y+half_size,
                   x-big_size, y+half_size,
                   x+size, y+half_size,
                   x+size+big_size, y+half_size,
                   x+half_size, y+size,
                   x+half_size, y+size+big_size,
                   x+half_size, y,
                   x+half_size, y-big_size)
        
        return shadow+inside+outside


    def move(self, x, y):
        x -= x % size
        y -= y % size
        if self.last != (x,y):
            self.vertex_list.vertices = self.vertices(x, y)


    def delete(self):
        self.vertex_list.delete()
        self.app.window.set_mouse_visible(True)
        self.app.window.pop_handlers()



class GameHandlers(object):
    def __init__(self, game):
        self.game = game
        game.app.window.push_handlers(self)

        
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
            elif symbol == key.C:
                self.game.toggle_cursor()
            elif symbol == key.W:
                self.game.wrapping = not self.game.wrapping


    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
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
        self.wrapping = True
        self.handlers = GameHandlers(self)
        self.cursor = Cursor(self)
        self.create(columns, rows)


    def toggle_cursor(self):
        if self.cursor is None:
            self.cursor = Cursor(self)
        else:
            self.cursor.delete()
            self.cursor = None


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

    def wrapped(self, x, y):
        if x >= self.columns:
            x -= self.columns
        elif x < 0:
            x += self.columns
        if y >= self.rows:
            y -= self.rows
        elif y < 0:
            y += self.rows 
        
        return (x, y)
    
    def draw_drag(self, x, y):
        if self.tk is None:
            try:
                x = x/size
                y = y/size

                if self.wrapping:
                    x, y = self.wrapped(x, y)

                now = (x, y)
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


    def clear_batch(self):
        try:
            for key in self.world:
                self.world[key].vertex_list.delete()
        except AttributeError:
            pass

    
    def create(self, columns, rows):
        self.clear_batch()

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
