
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from kivy.graphics import Color, Ellipse
from kivy.core.window import Window
from functools import partial

from random import random as rnd
import math as m


class Particle:
    def __init__(self, x, y, speed, size, id):
        self.color = [rnd(), rnd(), rnd()]
        self.pos = [x, y]
        self.vel = [2 * (rnd() - 0.5) * speed, 2 * (rnd() - 0.5) * speed]
        self.mass = size * (rnd() + 1)
        self.size = (self.mass, self.mass)
        self.id = id


class EvoCanvasApp(App):

    def check_collision(self, p1, p2):
        x1, y1 = p1.pos
        w1, h1 = p1.size
        x2, y2 = p2.pos
        w2, h2 = p2.size

        # if ((x1 + w1 >= x2 and x1 <= x2) or (x1 + w1 <= x2 + w2 and x1 >= x2 + w2)) and ((y1 + h1 >= y2 and y1 <= y2) or (y1 + h1 <= y2 + h2 and y1 >= y2 + h2)):
        #     return True
        r = (w1 + w2) / 2
        if ((x1 - x2)**2 + (y1 - y2)**2)**0.5 <= r:
            return True
        return False

    def draw(self):
        self.wid.canvas.clear()
        self.label.text = str(len(self.particles))
        with self.wid.canvas:
            for i in self.particles:
                Color(*i.color)
                Ellipse(pos=(i.pos[0] + self.wid.x, i.pos[1] + self.wid.y), size=i.size)

    def tick(self, dt):
        self.update_window_size()

        for i, p1 in enumerate(self.particles):
            for p2 in self.particles[i:]:
                if self.check_collision(p1, p2):
                    vel_1_tmp = [p2.mass * p2.vel[0] / p1.mass, p2.mass * p2.vel[1] / p1.mass]
                    vel_2_tmp = [p1.mass * p1.vel[0] / p2.mass, p1.mass * p1.vel[1] / p2.mass]

                    p1.vel, p2.vel = vel_1_tmp, vel_2_tmp

                    dx = 0
                    dy = 0
                    x1, y1 = p1.pos
                    x2, y2 = p2.pos

                    if x1 != x2:
                        g = m.atan(abs(y1-y2)/abs(x1-x2))
                    else:
                        g = m.pi * (-1, 1)[y1 > y2] / 2
                    dx = (m.cos(g)*(p1.size[0] / 2 + p2.size[0] / 2 - ((x1 - x2)**2 + (y1 - y2)**2)**0.5)) * (1, -1)[x2 > x1] / 2
                    dy = m.sin(m.atan(g))*(p1.size[0] / 2 + p2.size[0] / 2 - ((x1 - x2)**2 + (y1 - y2)**2)**0.5) * (1, -1)[y2 > y1] / 2
                    p1.pos = [p1.pos[0] + dx, p1.pos[1] + dy]
                    p2.pos = [p2.pos[0] - dx, p2.pos[1] - dy]

        for p in self.particles:
            p.pos = [p.pos[0] + p.vel[0], p.pos[1] + p.vel[1]]

            if p.pos[0] + p.size[0] > self.w:
                p.vel[0] *= -1
                p.pos[0] -= p.pos[0] + p.size[0] - self.w
            elif p.pos[0] < 0:
                p.vel[0] *= -1
                p.pos[0] -= p.pos[0]
            if p.pos[1] + p.size[1] > self.h:
                p.vel[1] *= -1
                p.pos[1] -= p.pos[1] + p.size[1] - self.h
            elif p.pos[1] < 0:
                p.vel[1] *= -1
                p.pos[1] -= p.pos[1]

        self.draw()
        Clock.schedule_once(self.tick)

    def add(self, n, *largs):
        self.particles += [Particle(rnd() * self.w, rnd() * self.h, self.speed, self.size, len(self.particles)) for _ in range(n)]

    def update_window_size(self):
        self.w, self.h = Window.size
        self.h -= 50

    def sub(self, n, *largs):
        if not n:
            n = len(self.particles)
        if len(self.particles) >= n:
            self.particles = self.particles[:-n]
        else:
            self.particles = []

    def build(self):
        self.speed = 3
        self.size = 20
        self.update_window_size()

        self.particles = [Particle(rnd() * self.w, rnd() * self.h, self.speed, self.size, i) for i in range(30)]

        self.wid = Widget(size=(self.w, self.h))

        self.label = Label(text='0')

        btn_add = Button(text='+ 10', on_press=partial(self.add, 10))
        btn_add1 = Button(text='+ 1', on_press=partial(self.add, 1))
        btn_sub = Button(text='- 10', on_press=partial(self.sub, 10))
        btn_clear = Button(text='Clear', on_press=partial(self.sub, 0))

        layout = BoxLayout(size_hint=(1, None), height=50)
        layout.add_widget(btn_add)
        layout.add_widget(btn_add1)
        layout.add_widget(btn_sub)
        layout.add_widget(btn_clear)
        layout.add_widget(self.label)

        root = BoxLayout(orientation='vertical')
        root.add_widget(self.wid)
        root.add_widget(layout)

        self.tick(0)

        return root


if __name__ == '__main__':
    EvoCanvasApp().run()
