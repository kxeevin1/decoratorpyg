import pygame
import random
import math
import importlib

W, H = 960, 640
FPS = 60
BG = (18, 20, 29)

AURA_TIME = 5000
MOUTH = (8, 24, 42, 24)

def load_decolorator():
    try:
        return importlib.import_module("decolorator")
    except:
        return None

decolorator = load_decolorator()

def blend(a, b, t):
    if decolorator:
        try:
            return decolorator.lerp(a, b, t)
        except:
            pass
    return tuple(int(a[i] + (b[i]-a[i]) * t) for i in range(3))

def pulse(color, t):
    return blend(color, (255,255,255), (math.sin(t*0.005)+1)/2)

AURAS = [
    ("aura1", (58,220,255)),
    ("aura2", (255,130,70)),
    ("aura3", (199,84,255))
]

class Power:
    def __init__(self, rect, aura):
        self.rect = rect
        self.aura = aura

    def draw(self, s, time):
        name, c = self.aura
        x,y = self.rect.center
        r = self.rect.w//2 - 4

        glow = pulse(c, time)
        pygame.draw.circle(s, (*glow,120), (x,y), r+5, 2)

        if name=="aura1":
            pygame.draw.circle(s, c, (x,y), r)
        elif name=="aura2":
            pygame.draw.rect(s, c, self.rect.inflate(-10,-10), border_radius=6)
        else:
            pygame.draw.polygon(s, c, [(x,y-r),(x+r,y),(x,y+r),(x-r,y)])


class Player:
    def __init__(self):
        self.rect = pygame.Rect(100,100,32,32)
        self.pos = pygame.Vector2(self.rect.topleft)

        self.dir = pygame.Vector2(1,0)
        self.speed = 180
        self.face = "right"

        self.anim = 0
        self.timer = 0

        self.auras = {}  # aura -> tiempo
        self.color = (252,219,57)

    def input(self, k):
        x = k[pygame.K_RIGHT]-k[pygame.K_LEFT]
        y = k[pygame.K_DOWN]-k[pygame.K_UP]

        if x!=0: y=0

        if x or y:
            self.dir.update(x,y)

            if x>0: self.face="right"
            elif x<0: self.face="left"
            elif y<0: self.face="up"
            elif y>0: self.face="down"

    def activate(self, aura, now):
        self.auras[aura] = now + AURA_TIME

    def update(self, dt, now):
        self.auras = {k:v for k,v in self.auras.items() if v>now}

        self.pos += self.dir*self.speed*dt

        self.pos.x = max(0, min(self.pos.x, W - self.rect.w))
        self.pos.y = max(0, min(self.pos.y, H - self.rect.h))

        if self.pos.x in (0, W - self.rect.w):
            self.dir.x = 0
        if self.pos.y in (0, H - self.rect.h):
            self.dir.y = 0

        self.rect.topleft = self.pos

        self.timer += dt
        if self.timer > 0.1:
            self.timer = 0
            self.anim = (self.anim+1)%4

    def draw(self, s, time):
        x,y = self.rect.center
        r = self.rect.w//2 - 2

        # AURAS (igual estilo original)
        for i,(aura,_) in enumerate(self.auras.items()):
            _,c = aura
            col = pulse(c, time)
            pygame.draw.circle(s, col, (x,y), r+6+i*5, 3)

        # cuerpo
        pygame.draw.circle(s, self.color, (x,y), r)

        ang = {"right":0,"up":math.pi/2,"left":math.pi,"down":-math.pi/2}[self.face]
        m = math.radians(MOUTH[self.anim])/2

        p1 = (x,y)
        p2 = (x+r*math.cos(ang-m), y-r*math.sin(ang-m))
        p3 = (x+r*math.cos(ang+m), y-r*math.sin(ang+m))

        pygame.draw.polygon(s, BG, (p1,p2,p3))
        pygame.draw.circle(s, (0,0,0), (x+5,y-8), 4)

        
class Game:
    def __init__(self):
        pygame.init()
        self.s = pygame.display.set_mode((W,H))
        self.c = pygame.time.Clock()

        self.p = Player()
        self.items = []
        self.spawn(10)

    def spawn(self,n):
        for _ in range(n):
            r = pygame.Rect(random.randint(0,W-40), random.randint(0,H-40),30,30)
            self.items.append(Power(r, random.choice(AURAS)))

    def pickups(self):
        now = pygame.time.get_ticks()
        for i in self.items[:]:
            if self.p.rect.colliderect(i.rect):
                self.p.activate(i.aura, now)
                self.items.remove(i)
                self.spawn(1)

    def run(self):
        while True:
            dt = self.c.tick(FPS)/1000

            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    return

            k = pygame.key.get_pressed()
            self.p.input(k)

            now = pygame.time.get_ticks()
            self.p.update(dt, now)

            self.pickups()

            self.s.fill(BG)

            for i in self.items:
                i.draw(self.s, now)

            self.p.draw(self.s, now)

            pygame.display.flip()


if __name__ == "__main__":
    Game().run()