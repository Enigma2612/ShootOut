import pygame, sys, os, random
pygame.init()
W,H = 1200, 700
WIN = pygame.display.set_mode((W,H), 528)
pygame.display.set_caption("SHOOT OUT!")
clock = pygame.time.Clock()
FPS = 60
game_over = False

def get_path(file):
    try:
        base_path = sys._MEIPASS
    except:
        base_path = os.path.abspath('.')
    return os.path.join(base_path, file)

time_font = pygame.font.Font(get_path("fixed_v02.ttf"), 18)
health_font = pygame.font.Font(get_path("fixed_v02.ttf"), 15)
winner_font = pygame.font.Font(get_path("fixed_v02.ttf"), 30)
subtext_font = pygame.font.Font(get_path('fixed_v02.ttf'), 15)
pause_font = pygame.font.Font(get_path('fixed_v02.ttf'), 15)
bul_w, bul_h = 10,5
p_vel = 5
bullet_vel = 7
frenzy_vel = 4
heart_vel = 2
hell_vel = 3
arrow_vel = 5
Frenzy_Event = pygame.USEREVENT + 1
Frenzy_Elapsed = 12000
Heart_Event = pygame.USEREVENT + 2
Heart_Elapsed = 10000
Hellfire_Event = pygame.USEREVENT + 3
Hellfire_Elapsed = 17000

#-------------Functions----------------------------#
def draw_text(surf, text, font, col, pos = (0,0), center = None, align = 'left', draw = True):
    img = font.render(text, True, col)
    rect = img.get_rect()
    if align.lower() == 'right': rect.topright = (surf.get_width() - pos[0], pos[1])
    else: rect.topleft = pos
    if center != None: rect.center = center
    if draw: surf.blit(img, rect)
    return img, rect


def load_image(name): return pygame.image.load(f"{get_path('data')}/{name}").convert_alpha()

def get_pic(name): return assets[name]

def handle_bullet_collisions(p1_bullets, p2_bullets):
    for i1, bullet in sorted(enumerate(p1_bullets), reverse = True):
        for i2, bullet2 in sorted(enumerate(p2_bullets), reverse = True):
            if bullet.rect.colliderect(bullet2.rect) or bullet2.rect.colliderect(bullet.rect):
                bullet.dead = True
                # p1_bullets.pop(i1)
                bullet2.dead = True
                # p2_bullets.pop(i2)
                collision_sfx.play()
                collision_rect = pygame.Rect(*bullet.rect.midright, 15, 15)
                return [5, collision_rect]
            
def handle_bullet_collisions2(p1_bullets, p2_bullets, collision_rects):
    for bullet in p1_bullets[:]:
        for bullet2 in p2_bullets[:]:
            if bullet.rect.colliderect(bullet2.rect):
                bullet.dead = True
                bullet2.dead = True
                collision_sfx.play()
                collision_rect = pygame.Rect(*bullet.rect.midright, 15, 15)
                collision_rects.append([5, collision_rect])
                            
def draw_pause(surf : pygame.Surface):
    t1 = 'Press p to continue'
    t2 = 'press esc to quit'
    cover = surf.copy()
    cover.set_alpha(200)
    cover.fill('grey10')
    surf.blit(cover, (0,0))

    draw_text(surf, t1, pause_font, 'green', center = (W//2, H//2 - 30))
    draw_text(surf, t2, pause_font, 'green', center = (W//2, H//2 + 30))

def reset():
    p1.reset()
    p2.reset()
    game_over = False
    pause = False
    frenzies, hearts, hells, arrows = [],[],[],[]
    ct = pygame.time.get_ticks()

    return game_over, pause, frenzies, hearts, hells, arrows, ct


#-------------Classes------------------------------#
class Player:
    def __init__(self, side, w, h, speed, controls, screen, border, col = 'red', imgs = None):
        self.screen = screen
        self.color = col
        self.speed = speed
        self.controls = controls
        self.border = border
        self.side = side
        self.max_health = 10
        self.health = self.max_health
        self.hurt  = 0
        self.frenzy = False
        self.bullets = []
        self.index = 0
        self.og_max_bullets = 5
        self.max_bullets = self.og_max_bullets

        if self.side == 'left':
            cx,cy = (0, self.screen.get_height()//2)
        elif self.side == 'right':
            cx,cy = (self.screen.get_width(), self.screen.get_height()//2)
        if imgs != None:
            self.images = [pygame.transform.scale(img, (w,h)).convert_alpha() for img in imgs] 
            self.rect = self.images[0].get_rect(center = (cx,cy))
            self.normal_image, self.tired_image, self.hurt_image, self.frenzy_image = self.images
            self.image = self.normal_image.copy()
            self.mask = pygame.mask.from_surface(self.image)
        else:
            self.rect = pygame.Rect(cx,cy,w,h)
            self.rect.center = (cx,cy)
    def update(self):
        dx,dy = 0,0
        up,down,left,right,shoot = self.controls
        keys = pygame.key.get_pressed()
        if keys[up]: dy -= self.speed
        if keys[down]: dy += self.speed
        if keys[left]: dx -= self.speed
        if keys[right]: dx += self.speed
        if self.side == 'left':
            if self.rect.right + dx >= self.border.left: dx = self.border.left - self.rect.right
            if self.rect.left + dx <= 0: dx = -self.rect.left
        elif self.side == 'right':
            if self.rect.left + dx <= self.border.right: dx = self.border.right - self.rect.left
            if self.rect.right + dx >= self.screen.get_width(): dx = self.screen.get_width() - self.rect.right
        if self.rect.top + dy <= 0: dy = -self.rect.top
        if self.rect.bottom + dy - 25> self.screen.get_height():
            dy = 0
            self.rect.bottom = self.screen.get_height() + 25
        self.rect.x += dx
        self.rect.y += dy
        if self.frenzy: self.max_bullets = 21
        else: self.max_bullets = self.og_max_bullets
        if self.hurt:
            self.hurt += 1
            self.hurt %= 30
            self.image = self.hurt_image.copy()
        elif len(self.bullets) == self.max_bullets: self.image = self.tired_image.copy()
        elif self.frenzy: self.image = self.frenzy_image.copy()
        else: self.image = self.normal_image.copy()

        self.mask = pygame.mask.from_surface(self.image)

    def handle_bullets(self, enemy):
        for index, bullet in sorted(enumerate(self.bullets), reverse = True):
            if bullet.dead: self.bullets.pop(index)
            else:
                bullet.update()
                # bullet.render()
            if enemy.mask.overlap(bullet.mask, (bullet.rect.x - enemy.rect.x, bullet.rect.y - enemy.rect.y)) and not bullet.dead:
                bullet.dead = True
                enemy.damage()
    
    def render_bullets(self): [bullet.render() for bullet in self.bullets]

    def render(self):
        if self.image != None: self.screen.blit(self.image, self.rect)
        else: pygame.draw.rect(self.screen, self.color, self.rect)

    def damage(self):
        self.health -= 1
        hit_sfx.play()
        self.hurt += 1
        self.frenzy = False

    def reset(self): self.__init__(self.side, self.normal_image.get_width(), self.normal_image.get_height(), self.speed, self.controls, self.screen, self.border, col = self.color, imgs = self.images)

class Bullet:
    def __init__(self, cx, cy, w, h, speed, screen, side = 'left', col = 'red'):
        self.image = pygame.Surface((w,h))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect(center = (cx,cy))
        self.screen = screen
        self.color = col
        self.side = side
        self.speed = speed
        self.dead = False
    def update(self):
        if self.rect.x < 0 and self.side == 'right': self.dead = True
        if self.rect.x > self.screen.get_width() and self.side == 'left': self.dead = True
        if self.side == 'right' and not self.dead: self.rect.x -= self.speed
        if self.side == 'left' and not self.dead: self.rect.x += self.speed      
    def render(self): pygame.draw.rect(self.screen, self.color, self.rect)
class Gamestate:
    def __init__(self):
        self.level = 'main' 
    def game(self):
        run = True
        game_over, pause, frenzies, hearts, hells, arrows, ct = reset()
        pygame.time.set_timer(Frenzy_Event, Frenzy_Elapsed)
        pygame.time.set_timer(Heart_Event, Heart_Elapsed)
        pygame.time.set_timer(Hellfire_Event, Hellfire_Elapsed)
        while run:
            WIN.blit(background_sprite, (0,0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p:
                        pause = not pause
                    if event.key == pygame.K_ESCAPE:
                        self.level = 'main'
                        run = False                    
                   
                    if not pause:
                        if event.key == p1.controls[-1]:
                            if not p1.frenzy:
                                bullet = Bullet(p1.rect.right, p1.rect.centery - 3, bul_w, bul_h, bullet_vel, WIN)
                                if len(p1.bullets) < p1.max_bullets:
                                    p1.bullets.append(bullet)
                                    shoot_sfx.play()
                            else:
                                bullet1 = Bullet(p1.rect.right, p1.rect.centery - 3 - 15, bul_w, bul_h, bullet_vel, WIN)
                                bullet2 = Bullet(p1.rect.right, p1.rect.centery - 3, bul_w, bul_h, bullet_vel, WIN)
                                bullet3 = Bullet(p1.rect.right, p1.rect.centery - 3 + 15, bul_w, bul_h, bullet_vel, WIN)
                                if len(p1.bullets) < p1.max_bullets:
                                    p1.bullets.extend([bullet1, bullet2, bullet3])
                                    shoot_sfx.play()
                        if event.key == p2.controls[-1]:
                            if not p2.frenzy:
                                bullet = Bullet(p2.rect.left, p2.rect.centery - 3, bul_w, bul_h, bullet_vel, WIN, side = 'right', col = 'cyan')
                                if len(p2.bullets) < p2.max_bullets:
                                    p2.bullets.append(bullet)
                                    shoot_sfx.play()
                            else:
                                bullet1 = Bullet(p2.rect.left, p2.rect.centery - 3 - 15, bul_w, bul_h, bullet_vel, WIN, side = 'right', col = 'cyan')
                                bullet2 = Bullet(p2.rect.left, p2.rect.centery - 3, bul_w, bul_h, bullet_vel, WIN, side = 'right', col = 'cyan')
                                bullet3 = Bullet(p2.rect.left, p2.rect.centery - 3 + 15, bul_w, bul_h, bullet_vel, WIN, side = 'right', col = 'cyan')
                                if len(p2.bullets) < p2.max_bullets:
                                    p2.bullets.extend([bullet1, bullet2, bullet3])
                                    shoot_sfx.play()
                        if event.key == pygame.K_RETURN:
                            if game_over:
                                game_over, pause, frenzies, hearts, hells, arrows, ct = reset()                    
                        if event.key == pygame.K_f:
                            pygame.event.post(pygame.event.Event(Frenzy_Event))
                        if event.key == pygame.K_h:
                            pygame.event.post(pygame.event.Event(Heart_Event))
                        if event.key == pygame.K_k:
                            pygame.event.post(pygame.event.Event(Hellfire_Event))
                if not pause:
                    if event.type == Frenzy_Event:
                        f = Frenzy(frenzy_sprite, 60, 60, frenzy_vel, WIN)
                        frenzies.append(f)                
                    if event.type == Heart_Event:
                        h = Heart(heart_sprite, 50, 50, heart_vel, WIN)
                        hearts.append(h)                
                    if event.type == Hellfire_Event:
                        k = Hellfire(skull_sprite, 50, 50, hell_vel, WIN)
                        hells.append(k)
            
            for f in frenzies[:]:
                if f.dead:
                    frenzies.remove(f)
                if not game_over and not pause:
                    f.update(players, p1.bullets + p2.bullets)
                f.render()   
            for h in hearts[:]:
                if h.dead:
                    hearts.remove(h)
                if not game_over and not pause:
                    h.update(players)
                h.render()   
            for k in hells[:]:
                if k.dead:
                    hells.remove(k)
                if not game_over and not pause:
                    arrows.extend(k.update(players))
                k.render() 
            for p in players:
                if not game_over and not pause:
                    p.update()
                p.render()    
            for arrow in arrows[:]:
                if not game_over and not pause:
                    arrow.update(players)
                arrow.render()
                if arrow.dead:
                    arrows.remove(arrow)
            if p1.health <= 0 or p2.health <= 0:
                game_over = True
            if not game_over and not pause:
                p1.handle_bullets(p2)
                p2.handle_bullets(p1)
                handle_bullet_collisions2(p1.bullets, p2.bullets, collisions)
                for index, (frames, rect) in sorted(enumerate(collisions), reverse = True):
                    if frames:
                        col_sprite = pygame.transform.scale(collision_sprite, (rect.width, rect.height))
                        WIN.blit(col_sprite, col_sprite.get_rect(center = rect.topleft))
                        frames -= 1
                        collisions[index] = (frames, rect)
                    else: collisions.pop(index)
            
            p1.render_bullets()
            p2.render_bullets()
            draw_text(WIN, f'Health: {p1.health}', health_font, col = 'white', pos = (20,20))
            draw_text(WIN, f'Health: {p2.health}', health_font, col = 'white', pos = (20,20), align = 'right')
            if not game_over and not pause:
                time = round((pygame.time.get_ticks() - ct)/1000)
            i,r = draw_text(WIN, f"Time: {time}", time_font, col = 'white', center = (W//2, H//2), draw = False)
            r.top = 20
            WIN.blit(i,r)

            if pause and not game_over:
                draw_pause(WIN)
                ct = pygame.time.get_ticks() - time*1000
                
            if game_over:
                if p1.health > p2.health: winner = 'RED WINS!'
                elif p2.health > p1.health: winner = 'BLUE WINS!'
                else: winner = 'DRAW'
                draw_text(WIN, f"{winner}", winner_font, col = 'green', center = (W//2, H//2-40))
                draw_text(WIN, f"press enter to restart", subtext_font, col = 'green', center = (W//2, H//2 + 40) )
            clock.tick(FPS)
            pygame.display.update()
    def rules(self):
        img = rules_cyan_sprite
        run = True
        while run:
            WIN.blit(img, (0,0))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.level = 'main'
                        run = False
            pygame.display.update()
            clock.tick(FPS)

    def main(self):
        run = True
        og_mus_vol = 0.4
        og_sfx_vol = 0.2
        mindex = 0
        sindex = 0
        dimension = 90
        music_button_sprites = [music_on_sprite, music_off_sprite, music_on_hover_sprite, music_off_hover_sprite]
        sfx_button_sprites = [sfx_on_sprite, sfx_off_sprite, sfx_on_hover_sprite, sfx_off_hover_sprite]
        left_click = False

    
        while run:
            WIN.fill('black')
            mpos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit(); sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    left_click = True            
            play_rect = play_sprite.get_rect(center = (W//2, H//2 - 30))
            rules_rect = rules_sprite.get_rect(centerx = W//2, top = play_rect.bottom + 20)
            music_rect = pygame.Rect(50, 50, dimension, dimension)
            sound_rect = pygame.Rect(50, 50, dimension, dimension)
            music_rect.y = sound_rect.y = play_rect.centery
            music_rect.right = play_rect.left
            sound_rect.left = play_rect.right + 20
            title_rect = title_sprite.get_rect(centerx = W//2, top = 0)
            if  play_rect.collidepoint(mpos):
                play_image = playhover_sprite
                if left_click:
                    self.level = 'game'
                    self.state_manager()
            else: play_image = play_sprite
            if rules_rect.collidepoint(mpos):
                rules_image = ruleshover_sprite
                if left_click:
                    self.level = 'rules'
                    self.state_manager()
            else: rules_image = rules_sprite
            if music_rect.collidepoint(mpos):
                if left_click:
                    if mindex in (0,1):
                        mindex = int(not(bool(mindex)))
                    else:
                        mindex = int(not(bool(mindex - 2))) + 2
                if mindex in (0,1): mindex += 2
            else:
                if mindex in (2,3): mindex -= 2
            if mindex in (1,3): mus_vol = 0
            else: mus_vol = og_mus_vol
            bgm.set_volume(mus_vol)
            music_image = pygame.transform.scale(music_button_sprites[mindex % 4], (music_rect.width + 20, music_rect.height + 20))
            if sound_rect.collidepoint(mpos):
                if left_click:
                    if sindex in (0,1):
                        sindex = int(not(bool(sindex)))
                    else:
                        sindex = int(not(bool(sindex - 2))) + 2
                if sindex in (0,1): sindex += 2
            else:
                if sindex in (2,3): sindex -= 2
            if sindex in (1,3): sfx_vol = 0
            else: sfx_vol = og_sfx_vol
            for sfx in sfxs: sfx.set_volume(sfx_vol)
            sound_image = pygame.transform.scale(sfx_button_sprites[sindex % 4], (sound_rect.width + 20, sound_rect.height + 20))
            WIN.blit(title_sprite, title_rect)
            WIN.blit(play_image, play_rect)
            WIN.blit(rules_image, rules_rect)
            WIN.blit(music_image, music_image.get_rect(center = music_rect.center))
            WIN.blit(sound_image, sound_image.get_rect(center = sound_rect.center))
            left_click = False
            pygame.display.update()
            clock.tick(FPS) 

    def state_manager(self):
        if self.level == 'game': self.game()
        elif self.level == 'rules': self.rules()
        else: self.main()

class Powerup:
    def __init__(self, image, w, h, speed, screen):
        self.image = pygame.transform.scale(image, (w,h)).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.bottom = 0
        self.screen = screen
        self.dead = False
        self.speed = speed
        self.mask = pygame.mask.from_surface(self.image)
    def update(self, players, bullets):
        self.rect.y += self.speed
        for player in players:
            if self.mask.overlap(player.mask, (player.rect.x - self.rect.x, player.rect.y - self.rect.y)) and not self.dead:
                self.dead = True
        for bullet in bullets:   
            if self.mask.overlap(bullet.mask, (bullet.rect.x - self.rect.x, bullet.rect.y - self.rect.y)) and not self.dead:
                bullet.dead = True
                self.dead = True
                hit_sfx.play()
    def render(self):
        if not self.dead:
            self.screen.blit(self.image, self.rect)

class Frenzy(Powerup):
    def __init__(self, image, w, h, speed, screen):
        Powerup.__init__(self, image, w, h, speed, screen)
        self.rect.x = random.randint(0,self.screen.get_width() - self.rect.width)
    def update(self, players, bullets):
        self.rect.y += self.speed
        for player in players:
            if self.mask.overlap(player.mask, (player.rect.x - self.rect.x, player.rect.y - self.rect.y)) and not self.dead:
                self.dead = True
                player.frenzy = True
                frenzy_gain_sfx.play()
        for bullet in bullets:   
            if self.mask.overlap(bullet.mask, (bullet.rect.x - self.rect.x, bullet.rect.y - self.rect.y)) and not self.dead:
                bullet.dead = True
                self.dead = True
                hit_sfx.play()
class Heart(Powerup):
    def __init__(self, image, w, h, speed, screen):
        Powerup.__init__(self, image, w, h, speed, screen)
        self.rect.centerx = self.screen.get_width()//2
    def update(self, players):
        self.rect.y += self.speed
        for player in players:
            if self.mask.overlap(player.mask, (player.rect.x - self.rect.x, player.rect.y - self.rect.y)) and not self.dead:
                self.dead = True
                player.health = min(player.health + 1, player.max_health)
                heart_gain_sfx.play()
class Hellfire(Powerup):
    def __init__(self, image, w, h, speed, screen):
        Powerup.__init__(self, image, w, h, speed, screen)
        self.rect.centerx = self.screen.get_width()//2
    def update(self, players): 
        self.rect.y += self.speed
        for index, player in enumerate(players):
            if self.mask.overlap(player.mask, (player.rect.x - self.rect.x, player.rect.y - self.rect.y)) and not self.dead:
                self.dead = True
                hellfire_gain_sfx.play()
                return self.rain(players[int(not index)])
        else: return []
    def rain(self, player):
        if player.side == 'left': 
            img = hellfire_blue_arrow_sprite
            x_bounds = (0, player.border.left - 20)
        elif player.side == 'right': 
            img = hellfire_red_arrow_sprite
            x_bounds = (player.border.right, self.screen.get_width() - 20)
        y_bounds = (-1000, -100)
        return [Arrow(img, random.randint(*x_bounds), random.randint(*y_bounds), 20, 30, arrow_vel, WIN) for _ in range(random.randint(15,25))]
class Arrow:
    def __init__(self, image, x, y, w, h, speed, screen):
        self.image = pygame.transform.scale(image, (w,h)).convert_alpha()
        self.speed = speed
        self.screen = screen
        self.rect = self.image.get_rect(topleft = (x,y))
        self.mask = pygame.mask.from_surface(self.image)
        self.dead = False
    def update(self, players):
        if self.rect.y > self.screen.get_height():
            self.dead = True
        else: self.rect.y += self.speed
        for p in players:
            if self.mask.overlap(p.mask, (p.rect.x - self.rect.x, p.rect.y - self.rect.y)) and not self.dead:
                self.dead = True
                p.damage()        
    def render(self):
        self.screen.blit(self.image, self.rect)

#-------------General------------------------------#

wasd = [eval(f"pygame.K_{i}") for i in ['w','s','a','d','LSHIFT']]
arrow_keys = [eval(f"pygame.K_{i}") for i in ['UP', 'DOWN', 'LEFT', 'RIGHT', 'RALT']]


assets = {f"{i.partition('.')[0]}_sprite":load_image(f"{i}").convert_alpha() for i in os.listdir(get_path('data')) if i.partition('.')[-1] in ['jpg', 'jpeg', 'png']}

for i in assets: exec(f"{i} = assets['{i}']")

bgm = pygame.mixer.Sound(f'{get_path('data')}/bgm.mp3')
sfx_files = [i for i in os.listdir(get_path('data')) if i.partition('.')[-1] in ['wav', 'mp3']]
sfx_files.remove('bgm.mp3')
sfxs = []
for i in sfx_files: 
    exec(f"{i.partition('.')[0]}_sfx = pygame.mixer.Sound('{get_path('data')}/{i}')")
    sfxs.append(eval(f"{i.partition('.')[0]}_sfx"))
for sfx in sfxs: sfx.set_volume(0.2)
bgm.set_volume(0.4)
bgm.play(-1)
border = pygame.Rect(0,0,10,H)
border.centerx = W//2
p1 = Player('left', 100, 100, p_vel, wasd, WIN, border, col = 'red', imgs = [red_normal_sprite, red_limit_sprite, red_hurt_sprite, red_frenzy_sprite])
p2 = Player('right', 100, 100, p_vel, arrow_keys, WIN, border, col = 'cyan', imgs = [blue_normal_sprite, blue_limit_sprite, blue_hurt_sprite, blue_frenzy_sprite])
players = [p1,p2]
collisions = []
while True: Gamestate().state_manager()