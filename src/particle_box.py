## python -m PyInstaller particle_box.spec

from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from kivy.graphics import Color, Ellipse, Rectangle, Mesh, Line
from kivy.core.window import Window

import threading
from functools import partial
from random import random as rnd
import math as m


class Particle:
    def __init__(self, x, y, speed, size, id, w, h):
        self.color = [x / w, y / w, 1]
        self.pos = [x, y]
        self.vel = [(2 * rnd() - 1) * speed, (2 * rnd() - 1) * speed]
        self.mass = size * (rnd() + 1)
        self.size = (self.mass, self.mass)
        self.id = id
        self.hover = False

    def check_collision(self, p):
        x1, y1 = self.pos
        w1, h1 = self.size
        x2, y2 = p.pos
        w2, h2 = p.size

        if (x1 - x2 + (w1 - w2) / 2)**2 + (y1 - y2 + (h1 - h2) / 2)**2 <= (w1 + w2)**2 / 4:
            return True
        return False


class Polygon:
    def __init__(self, pts, id):
        self.color = [rnd(), rnd(), 1]
        self.vertex = pts[:]
        self.normal = []
        for i in range(len(pts)):
            j = (i + 1) % len(pts)
            norm = m.sqrt((pts[i][0] - pts[j][0])**2 + (pts[i][1] - pts[j][1])**2)
            self.normal += [((pts[j][1] - pts[i][1]) / norm, (pts[i][0] - pts[j][0]) / norm)]

        self.id = id

    def check_collision(self, p):
        pw, ph = p.size
        px, py = p.pos[0] + pw / 2, p.pos[1] + ph / 2

        d = []
        l = []
        hit = []
        for i in range(len(self.vertex)):
            j = (i + 1) % len(self.vertex)
            x0, y0 = (self.vertex[i][0] + self.vertex[j][0]) / 2, (self.vertex[i][1] + self.vertex[j][1]) / 2
            if self.normal[i][1] != 0:
                m_1 = - self.normal[i][0] / self.normal[i][1]
                b_2 = self.vertex[i][1] - m_1 * self.vertex[i][0]
                d += [abs(-m_1 * px + py - b_2) / m.sqrt(1 + m_1**2)]

                if m_1 != 0:
                    m_2 = -1 / m_1
                    b_2 = y0 - m_2 * x0
                    l += [abs(-m_2 * px + py - b_2) / m.sqrt(1 + m_2**2)]
                else:
                    l += [abs(x0 - px)]
            else:
                d += [abs(x0 - px)]
                l += [abs(y0 - py)]

            w = m.sqrt((self.vertex[i][0] - self.vertex[j][0])**2 + (self.vertex[i][1] - self.vertex[j][1])**2)
            hit += [0]
            if d[i] <= pw / 2 and l[i] <= w / 2 + pw / 2:
                hit[i] = 1

        s = sum(hit)
        if s == 0:
            return False
        for i in range(len(self.vertex)):
            if s == 1:
                if hit[i]:
                    return (i, pw / 2 - d[i] + 1)
            if s > 1:
                j = (i + 1) % len(self.vertex)
                if hit[i] and hit[j]:
                    if self.normal[i][0]*p.vel[0] + self.normal[i][1]*p.vel[1] < self.normal[j][0]*p.vel[0] + self.normal[j][1]*p.vel[1]:
                        return (i, 1)
                    return (j, 1)

class ParticleBox(App):
    def draw(self):
        self.wid.canvas.clear()
        with self.wid.canvas:
            for t in self.polygons:
                p = []
                indices = []
                for i in range(len(t.vertex)):
                    j = (i + 1) % len(t.vertex)
                    p += [t.vertex[i][0] + self.wid.x, t.vertex[i][1] + self.wid.y, 0, 0]
                    indices += [i]
                    if self.show_norms:
                        Color((1, 1, 1))
                        Line(points=[(t.vertex[i][0] + t.vertex[j][0]) / 2 + self.wid.x,
                                       (t.vertex[i][1] + t.vertex[j][1]) / 2 + self.wid.y,
                                       (t.vertex[i][0] + t.vertex[j][0]) / 2 + t.normal[i][0] * 20 + self.wid.x,
                                       (t.vertex[i][1] + t.vertex[j][1]) / 2 + t.normal[i][1] * 20 + self.wid.y], width=2)
                Color(*t.color)
                Mesh(vertices=p, indices=indices, mode='triangle_fan')

            for i in self.particles:
                if i.hover or i.id == self.selected:
                    Color(1, 1, 1)
                    Ellipse(pos=(i.pos[0] + self.wid.x - 2, i.pos[1] + self.wid.y - 2), size=(i.size[0] + 4, i.size[1] + 4))
                Color(*i.color)
                Ellipse(pos=(i.pos[0] + self.wid.x, i.pos[1] + self.wid.y), size=i.size)

    def p_collision(self, p1, p2):
        if p1.check_collision(p2):
            x1, y1 = p1.pos
            x2, y2 = p2.pos
            w1, h1 = p1.size
            w2, h2 = p2.size

            m1 = p2.mass / p1.mass
            m2 = p1.mass / p2.mass

            p1.vel, p2.vel = [m1 * p2.vel[0] * self.e_loss,
                              m1 * p2.vel[1] * self.e_loss], [m2 * p1.vel[0] * self.e_loss,
                              m2 * p1.vel[1] * self.e_loss]

            if x1 != p2.pos[0]:
                g = m.atan(abs(y1 - y2) / abs(x1 - x2))
            else:
                g = m.pi * (-1, 1)[y1 > y2] / 2

            d = ((h1 + h2) / 2 - m.sqrt((x1 - x2 + (w1 - w2) / 2)**2 + (y1 - y2 + (h1 - h2) / 2)**2)) / 2
            dx = m.cos(g) * d * (1, -1)[x2 > x1] + 1
            dy = m.sin(g) * d * (1, -1)[y2 > y1] + 1
            p1.pos = [p1.pos[0] + dx, p1.pos[1] + dy]
            p2.pos = [p2.pos[0] - dx, p2.pos[1] - dy]

    def t_collision(self, p, t):
        v = t.check_collision(p)
        if v:
            n = t.normal[v[0]]

            n_dot_v = n[0] * p.vel[0] + n[1] * p.vel[1]

            p.vel[0] = (p.vel[0] - 2 * n[0] * n_dot_v) * self.e_loss
            p.pos[0] += n[0] * v[1]
            p.vel[1] = (p.vel[1] - 2 * n[1] * n_dot_v) * self.e_loss
            p.pos[1] += n[1] * v[1]

    def wall_collision(self, p1):
        if p1.pos[0] + p1.size[0] > self.w:
            p1.vel[0] *= -1 * self.e_loss
            p1.pos[0] -= p1.pos[0] + p1.size[0] - self.w
        elif p1.pos[0] < 0:
            p1.vel[0] *= -1 * self.e_loss
            p1.pos[0] -= p1.pos[0]
        if p1.pos[1] + p1.size[1] > self.h:
            p1.vel[1] *= -1 * self.e_loss
            p1.pos[1] -= p1.pos[1] + p1.size[1] - self.h
        elif p1.pos[1] < 0:
            p1.vel[1] *= -1 * self.e_loss
            p1.pos[1] -= p1.pos[1]

    def tick(self, dt):
        self.update_window_size()

        for i, p1 in enumerate(self.particles):
            for p2 in self.particles[i + 1:]:
                self.p_collision(p1, p2)

            for t in self.polygons:
                self.t_collision(p1, t)

            mx = self.mouse[0] - self.wid.x
            my = self.mouse[1] - self.wid.y
            if m.sqrt((mx - p1.pos[0] - p1.size[0] / 2)**2 + (my - p1.pos[1] - p1.size[1] / 2)**2) < p1.size[0]:  # p1.size[0] / 2 for accuracy
                p1.hover = True
                if self.clicked and self.selected == -1:
                    self.selected = p1.id
                    self.clicked = False
            else:
                p1.hover = False

            if self.selected == p1.id or self.ctrl:
                p1.vel = [self.mouse[0] - self.prev_mouse[0], self.mouse[1] - self.prev_mouse[1]]

            p1.pos = [p1.pos[0] + p1.vel[0], p1.pos[1] + p1.vel[1]]

            self.wall_collision(p1)

            if self.grav:
                p1.vel[1] -= 0.2
                p1.vel[1] *= self.inelasticity

        self.draw()

        if dt:
            self.label2.text = str(int(1/dt)) + ' FPS'

        self.dt = dt
        Clock.schedule_once(self.tick)

    def add(self, n, *largs):
        self.particles += [Particle(rnd() * self.w, rnd() * self.h, self.speed,
                           self.size, len(self.particles) + i, self.w, self.h) for i in range(n)]
        self.label1.text = str(len(self.particles))

    def sub(self, n, *largs):
        if not n:
            n = len(self.particles)
        if len(self.particles) >= n:
            self.particles = self.particles[:-n]
        else:
            self.particles = []
        self.label1.text = str(len(self.particles))

    def set_mouse_pos(self, p, dt=0):
        self.pos_schedule.cancel()
        self.prev_mouse = self.mouse[:]
        self.mouse = p
        self.pos_schedule = Clock.schedule_once(self.update_mouse, 0.1)

    def update_mouse(self, dt):
        self.set_mouse_pos(self.mouse)

    def update_window_size(self):
        self.w, self.h = Window.size
        self.h -= 50

    def on_mouse_down(self, *args):
        self.clicked = True

    def on_mouse_up(self, *args):
        for i in self.particles:
            if i.id == self.selected:
                i.vel[0] = self.mouse[0] - self.prev_mouse[0]
                i.vel[1] = self.mouse[1] - self.prev_mouse[1]
        self.clicked = False
        self.selected = -1

    def on_key_down(self, *args):
        if args[1] == 305:
            self.ctrl = True
        if args[1] == 304:
            self.grav = True
        if args[1] == 308:
            self.e_loss = self.inelasticity
        if args[1] == 110:
            self.show_norms = True

    def on_key_up(self, *args):
        if args[1] == 305:
            self.ctrl = False
        if args[1] == 304:
            self.grav = False
        if args[1] == 308:
            self.e_loss = 1
        if args[1] == 110:
            self.show_norms = False

    def build(self):
        self.clicked = False
        self.selected = -1
        self.speed = 3
        self.size = 20
        self.inelasticity = 0.95
        self.grav = False
        self.mouse = (0, 0)
        self.ctrl = False
        self.e_loss = 1
        self.show_norms = False
        Window.bind(mouse_pos=lambda w, p: self.set_mouse_pos(p))
        Window.bind(on_touch_down=self.on_mouse_down)
        Window.bind(on_touch_up=self.on_mouse_up)
        Window.bind(on_key_down=self.on_key_down)
        Window.bind(on_key_up=self.on_key_up)
        self.pos_schedule = Clock.schedule_once(self.update_mouse, 0.1)
        self.update_window_size()

        self.polygons = [Polygon([(200, 200), (250, 200), (200, 250)], 0),
                          Polygon([(400, 400), (480, 420), (380, 450)], 1),
                          Polygon([(560, 50), (680, 120), (550, 250)], 1),
                          Polygon([(100, 100), (150, 50), (200, 100), (200, 130), (100, 130)], 1)]

        self.particles = []

        self.wid = Widget(size=(self.w, self.h))

        self.label1 = Label(text='0')
        self.label2 = Label(text='0 FPS')

        self.add(100)

        layout = BoxLayout(size_hint=(1, None), height=50)
        layout.add_widget(Button(text='+ 10', on_press=partial(self.add, 10)))
        layout.add_widget(Button(text='+ 1', on_press=partial(self.add, 1)))
        layout.add_widget(Button(text='- 10', on_press=partial(self.sub, 10)))
        layout.add_widget(Button(text='Clear', on_press=partial(self.sub, 0)))
        layout.add_widget(self.label1)
        layout.add_widget(self.label2)

        root = BoxLayout(orientation='vertical')
        root.add_widget(self.wid)
        root.add_widget(layout)

        self.tick(0)
        threading.Thread(target=self.draw).start()

        return root


if __name__ == '__main__':
    ParticleBox().run()
