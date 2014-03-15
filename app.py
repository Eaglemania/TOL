import pyglet, config
from pyglet.window import key


"""
    KEYS:
    
        ESC - close window
        F - toggle fps counter
        M - maximize fps (even if there is nothing new to draw, draw the same things again. i think there is less stutter)
        V - toggle vsync (not only affects draw event but all scheduled events running above vsync fps i think, thus crippeling simulations etc)

    yeaaahhh.....
"""


def spam(dt):
    #for spamming the pyglet event loop with.
    #to force max amount of draw events?
    #there is alot of strangeness here, sometimes when i toggle it it works great tho
    pass

class App:
    
    def __init__(self):
        self.window = pyglet.window.Window(width = config.width,
                                           height = config.height,
                                           vsync = config.vsync,
                                           resizable = config.resizable)

        self.batch = pyglet.graphics.Batch()
        self.sprite_group = pyglet.graphics.OrderedGroup(0)
        self.text_group = pyglet.graphics.OrderedGroup(1)
        self.fps_display = pyglet.clock.ClockDisplay()
        
        self.drawables = [self.batch]

        self.max_fps(config.max_fps)
        self.show_fps(config.show_fps)
        #have to go to fullscreen now to get the new, right resolution.
        #in pyglet.window init it'll go to fullscreen but keep the resolution from the init
        #which is normal i guess... but for now, the resolution will change.
        self.fullscreen(config.fullscreen)

        @self.window.event
        def on_close():
            self.save_config()
            
        @self.window.event
        def on_draw():
            self.window.clear()
            for thing in self.drawables:
                thing.draw()
                
        @self.window.event
        def on_key_press(symbol, modifiers):
            if symbol == key.F:
                self.show_fps(not config.show_fps)
            elif symbol == key.M:
                self.max_fps(not config.max_fps)
            elif symbol == key.V:
                self.vsync(not config.vsync)
            elif symbol == key.ENTER:
                self.fullscreen(not config.fullscreen)


    def rebatch(self):
        if self.batch in self.drawables:
            self.drawables.remove(self.batch)
        self.batch = pyglet.graphics.Batch()
        self.drawables.append(self.batch)
        
        if self.fps_display in self.drawables:
            self.drawables.remove(self.fps_display)
        self.drawables.append(self.fps_display)
        
        @self.window.event
        def on_draw():
            self.window.clear()
            for thing in self.drawables:
                thing.draw()

                
    def save_config(self):
        with open("config.py", "w") as f:
            f.write("#will be completly overwritten on config save ;( not just the values")
            f.write("\nwidth = " + str(config.width))
            f.write("\nheight = " + str(config.height))
            f.write("\nvsync = " + str(config.vsync))
            f.write("\nfullscreen = " + str(config.fullscreen))
            f.write("\nmax_fps = " + str(config.max_fps))
            f.write("\nshow_fps = " + str(config.show_fps))
            f.write("\n#can't be toggled, needs app restart")
            f.write("\nresizable = " + str(config.resizable))
            f.close()


    def run(self):
        pyglet.app.run()


    def max_fps(self, flag):
        print "max_fps", flag
        if flag:
            pyglet.clock.schedule(spam)
        else:
            pyglet.clock.unschedule(spam)
        config.max_fps = flag


    def show_fps(self, flag):
        print "show_fps", flag
        if flag:
            if self.fps_display not in self.drawables:
                self.drawables.append(self.fps_display)
        else:
            if self.fps_display in self.drawables:
                self.drawables.remove(self.fps_display)      
        config.show_fps = flag


    def vsync(self, flag):
        print "vsync", flag
        self.window.set_vsync(flag)
        config.vsync = flag


    def fullscreen(self, flag):
        print "fullscreen", flag
        self.window.set_fullscreen(flag)
        config.fullscreen = flag
