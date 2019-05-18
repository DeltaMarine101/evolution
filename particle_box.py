from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from kivy.graphics import Color, Ellipse, Rectangle, Triangle, Bezier
from kivy.core.window import Window

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


class Block:
    def __init__(self, x, y, w, h, id):
        self.color = [rnd(), rnd(), 1]
        self.faces = [[x, y + h/2], [x + w, y + h/2], [x + w/2, y], [x + w/2, y + h]]
        self.normal = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        self.pos = [x, y]
        self.size = (w, h)
        self.id = id

    def check_collision(self, p):
        px, py = p.pos
        pw, ph = p.size
        bx, by = self.pos
        bw, bh = self.size

        if px > bx + bw:
            return False
        if px + pw < bx:
            return False
        if py > by + bh:
            return False
        if py + ph < by:
            return False
        return True


class Polygon3:
    def __init__(self, x0, y0, x1, y1, x2, y2, id):
        self.color = [rnd(), rnd(), 1]
        self.vertex = [[x0, y0], [x1, y1], [x2, y2]]
        norm = [m.sqrt((x0 - x1)**2 + (y0 - y1)**2), m.sqrt((x1 - x2)**2 + (y1 - y2)**2), m.sqrt((x2 - x0)**2 + (y2 - y0)**2)]
        self.normal = [((y1 - y0) / norm[0], (x0 - x1) / norm[0]),
                        ((y2 - y1) / norm[1], (x1 - x2) / norm[1]),
                        ((y0 - y2) / norm[2], (x2 - x0) / norm[2])]
        self.id = id

    def check_collision(self, p):
        pw, ph = p.size
        px, py = p.pos[0] + pw / 2, p.pos[1] + ph / 2

        x0, y0 = (self.vertex[0][0] + self.vertex[1][0]) / 2, (self.vertex[0][1] + self.vertex[1][1]) / 2
        if self.normal[0][1] != 0:
            m_1 = - self.normal[0][0] / self.normal[0][1]
            b = self.vertex[0][1] - m_1 * self.vertex[0][0]
            d0 = abs(-m_1 * px + py - b) / m.sqrt(1 + m_1**2)

            if m_1 != 0:
                m_2 = -1 / m_1
                b_2 = y0 - m_2 * x0
                l0 = abs(-m_2 * px + py - b_2) / m.sqrt(1 + m_2**2)
            else:
                l0 = abs(x0 - px)
        else:
            d0 = abs(x0 - px)
            l0 = abs(y0 - py)

        x1, y1 = (self.vertex[1][0] + self.vertex[2][0]) / 2, (self.vertex[1][1] + self.vertex[2][1]) / 2
        if self.normal[1][1] != 0:
            m_1 = - self.normal[1][0] / self.normal[1][1]
            b = self.vertex[1][1] - m_1 * self.vertex[1][0]
            d1 = abs(-m_1 * px + py - b) / m.sqrt(1 + m_1**2)

            if m_1 != 0:
                m_2 = -1 / m_1
                b_2 = y1 - m_2 * x1
                l1 = abs(-m_2 * px + py - b_2) / m.sqrt(1 + m_2**2)
            else:
                l1 = abs(x1 - px)
        else:
            d1 = abs(x1 - px)
            l1 = abs(y1 - py)

        x2, y2 = (self.vertex[2][0] + self.vertex[0][0]) / 2, (self.vertex[2][1] + self.vertex[0][1]) / 2
        if self.normal[2][1] != 0:
            m_1 = - self.normal[2][0] / self.normal[2][1]
            b = self.vertex[2][1] - m_1 * self.vertex[2][0]
            d2 = abs(-m_1 * px + py - b) / m.sqrt(1 + m_1**2)

            if m_1 != 0:
                m_2 = -1 / m_1
                b_2 = y2 - m_2 * x2
                l2 = abs(-m_2 * px + py - b_2) / m.sqrt(1 + m_2**2)
            else:
                l2 = abs(x2 - px)
        else:
            d2 = abs(x2 - px)
            l2 = abs(y2 - py)

        hit = [0, 0, 0]
        w0 = m.sqrt((self.vertex[0][0] - self.vertex[1][0])**2 + (self.vertex[0][1] - self.vertex[1][1])**2)
        if d0 <= pw / 2 and l0 <= w0 / 2 + pw / 2:
            hit[0] = 1
        w1 = m.sqrt((self.vertex[1][0] - self.vertex[2][0])**2 + (self.vertex[1][1] - self.vertex[2][1])**2)
        if d1 <= pw / 2 and l1 <= w1 / 2 + pw / 2:
            hit[1] = 1
        w2 = m.sqrt((self.vertex[0][0] - self.vertex[2][0])**2 + (self.vertex[0][1] - self.vertex[2][1])**2)
        if d2 <= pw / 2 and l2 <= w2 / 2 + pw / 2:
            hit[2] = 1
        s = sum(hit)
        if s == 0:
            return False
        if s == 1:
            if hit[0]:
                return (0, pw / 2 - d0 + 1)
            if hit[1]:
                return (1, pw / 2 - d1 + 1)
            return (2, pw / 2 - d2 + 1)

        n0 = self.normal[0]
        n1 = self.normal[1]
        n2 = self.normal[2]
        if hit[0] and hit[1]:
            if n0[0] * p.vel[0] + n0[1] * p.vel[1] < n1[0] * p.vel[0] + n1[1] * p.vel[1]:
                return (0, pw / 2 - d0 + 1)
            return (1, pw / 2 - d1 + 1)
        if hit[1] and hit[2]:
            if n1[0] * p.vel[0] + n1[1] * p.vel[1] < n2[0] * p.vel[0] + n2[1] * p.vel[1]:
                return (1, pw / 2 - d1 + 1)
            return (2, pw / 2 - d2 + 1)
        if hit[2] and hit[0]:
            if n2[0] * p.vel[0] + n2[1] * p.vel[1] < n0[0] * p.vel[0] + n0[1] * p.vel[1]:
                return (0, pw / 2 - d0 + 1)
            return (2, pw / 2 - d2 + 1)

class ParticleBox(App):
    def draw(self):
        self.wid.canvas.clear()
        with self.wid.canvas:
            for i in self.triangles:
                Color(*i.color)
                Triangle(points=([i.vertex[0][0] + self.wid.x, i.vertex[0][1] + self.wid.y,
                                 i.vertex[1][0] + self.wid.x, i.vertex[1][1] + self.wid.y,
                                 i.vertex[2][0] + self.wid.x, i.vertex[2][1] + self.wid.y]))
                Color((1, 1, 1))
                if self.show_norms:
                    Bezier(points=[(i.vertex[0][0] + i.vertex[1][0]) / 2 + self.wid.x,
                                   (i.vertex[0][1] + i.vertex[1][1]) / 2 + self.wid.y,
                                   (i.vertex[0][0] + i.vertex[1][0]) / 2 + i.normal[0][0] * 20 + self.wid.x,
                                   (i.vertex[0][1] + i.vertex[1][1]) / 2 + i.normal[0][1] * 20 + self.wid.y])
                    Bezier(points=[(i.vertex[1][0] + i.vertex[2][0]) / 2 + self.wid.x,
                                   (i.vertex[1][1] + i.vertex[2][1]) / 2 + self.wid.y,
                                   (i.vertex[1][0] + i.vertex[2][0]) / 2 + i.normal[1][0] * 20 + self.wid.x,
                                   (i.vertex[1][1] + i.vertex[2][1]) / 2 + i.normal[1][1] * 20 + self.wid.y])
                    Bezier(points=[(i.vertex[2][0] + i.vertex[0][0]) / 2 + self.wid.x,
                                   (i.vertex[2][1] + i.vertex[0][1]) / 2 + self.wid.y,
                                   (i.vertex[2][0] + i.vertex[0][0]) / 2 + i.normal[2][0] * 20 + self.wid.x,
                                   (i.vertex[2][1] + i.vertex[0][1]) / 2 + i.normal[2][1] * 20 + self.wid.y])
            for i in self.blocks:
                Color(*i.color)
                Rectangle(pos=(i.pos[0] + self.wid.x, i.pos[1] + self.wid.y), size=i.size)
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
            dx = m.cos(g) * d * (1, -1)[x2 > x1]
            dy = m.sin(g) * d * (1, -1)[y2 > y1]
            p1.pos = [p1.pos[0] + dx, p1.pos[1] + dy]
            p2.pos = [p2.pos[0] - dx, p2.pos[1] - dy]

    def b_collision(self, p, b):
        if b.check_collision(p):
            t = [(p.pos[0] + p.size[0] / 2 - i[0])**2 + (p.pos[1] + p.size[1] / 2 - i[1])**2 for i in b.faces]
            n = b.normal[t.index(min(t))]
            f = b.faces[t.index(min(t))]

            n_dot_v = n[0] * p.vel[0] + n[1] * p.vel[1]

            p.vel[0] = (p.vel[0] - 2 * n[0] * n_dot_v) * self.e_loss
            p.pos[0] += n[0] * (min([abs(f[0] - p.pos[0]), abs(f[0] - p.pos[0] - p.size[0])]) + 1)
            p.vel[1] = (p.vel[1] - 2 * n[1] * n_dot_v) * self.e_loss
            p.pos[1] += n[1] * (min([abs(f[1] - p.pos[1]), abs(f[1] - p.pos[1] - p.size[1])]) + 1)

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

            for b in self.blocks:
                self.b_collision(p1, b)

            for t in self.triangles:
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

        self.triangles = [Polygon3(200, 200, 250, 200, 200, 250, 0),
                          Polygon3(400, 400, 480, 420, 380, 450, 1),
                          Polygon3(560, 50, 680, 120, 550, 250, 1)]
        self.blocks = []#[Block(200, 200, 200, 200, 0)]

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

        return root


if __name__ == '__main__':
    ParticleBox().run()
