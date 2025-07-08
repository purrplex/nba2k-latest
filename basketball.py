import pygame
from team_bots import TeamBots
from opp_bots import OppBots

# Their curls cascade, a silken sight,
# Like sunlit waves, both dark and bright.
# I wonder if each curl holds a story,
# A love song whispered, full of glory.
# Their laughter rings, a sweet refrain,
# That dances through their curly mane.
# I asked them once, "Do they get in your way?"
# They smiled, "Only when they lead me to you each day!"
# Their curls surround, a soft embrace,
# Like gentle tendrils, finding their place.
# I said their hair was a masterpiece to behold,
# They blushed, "Just like your heart, brave and bold."
# Their hair's a mystery, a tangled art,
# But in their eyes, I see my counterpart.
# And though I may try to make silly jokes,
# My heart's the only truth this poem evokes.


class Basketball(pygame.sprite.Sprite):
    #def __init__(self, pos, player, time, direction, shootpower = 1):
    def __init__(self, data):
        super().__init__(data.get('group'))

        player = data.get('player')
        self.player = player
        self.original_image = pygame.image.load("images/basketball.png").convert_alpha()
        self.image = self.original_image
        self.rect = self.image.get_rect(center=data.get('pos'))
        self.pos = pygame.math.Vector2(self.rect.midleft)
        self.start_pos = pygame.math.Vector2(self.rect.midleft)
        self.direction = data.get('direction')
        #self.direction.y *= 0.5
        self.shootpower = data.get('shootpower', 1)
        self.point_value = data.get('point_value', 1)
        self.on_score = data.get('score')
        self.on_rebound = data.get('rebound')
        self.on_catch = data.get('catch')
        self.shooting = data.get('action') == "shoot"
        
        if not self.shooting:
            self.pos.y += abs(self.direction.y) * 200
                

        self.group = data.get('group')

        self.speed = 400
        self.menu = False
        self.collision_state = None
        self.bounces = 0
        self.hoop_bounces = 0
        self.backboard = {}
        self.backboard['right'] = pygame.Rect(1920, 200, 1, 110)
        self.backboard['left'] = pygame.Rect(280, 200, 1, 110)
        self.hoop_coords = {}
        self.hoop_coords['right'] = pygame.math.Vector2(1850, 350)
        self.hoop_coords['left'] = pygame.math.Vector2(310, 350)
        self.scored_side = None
            
        self.height = 0
        self.velocity = 0
        self.jump_speed = 400
        self.jump_start = 1
        self.gravity = -800

        self.velocity = self.jump_speed
        self.height = self.jump_start
        self.ceiling = 0
        self.last_pos = self.pos.copy()

        self.scale_factor = self.player.scale_factor
        
        self.last_hoop_distance = float('inf')
        
    def remove(self):
        for group in self.groups():
            group.remove(self)
        
    def scored(self):
        self.remove()
        ball_info = {
            'player':self.player,
            'side':self.scored_side
        }
        difference_vec = (self.start_pos - self.hoop_coords[self.scored_side])
        ball_info['distance'] = difference_vec
        self.on_score(ball_info)
    
    def rebound(self):
        self.remove()
        self.on_rebound(pygame.math.Vector2(self.pos.x, self.pos.y - self.height))
        
    def catch(self, players):
        self.remove()
        player = players[0]
        self.on_catch(pygame.math.Vector2(self.pos.x, self.pos.y - self.height), player)
    
    def out_of_bounds(self):
        pass
        
    def scale(self):
        #self.scale_factor = max(1.0, min(1.5, 1 + (self.pos.y - 400) / 500))
        self.scale_factor = max(0.5, (self.pos.y - 462)/213 * 0.5 + 1.5)
        width, height = self.original_image.get_size()
        new_width = int(width * self.scale_factor)
        new_height = int(height * self.scale_factor)

        if new_width != self.rect.width or new_height != self.rect.height:
            self.image = pygame.transform.scale(
                self.original_image, (new_width, new_height)
            )
            self.rect = self.image.get_rect(center=self.rect.center)
            
    def hoop_detection(self, dt, left_side=False):
        if left_side:
            self.scored_side = "left"
        else:
            self.scored_side = "right"
            
        if self.rect.colliderect(self.backboard[self.scored_side]):
            self.direction.x *= -0.67
            self.direction.y *= 0.5
            self.pos = self.last_pos.copy()
            #self.pos.x += self.direction.x
            self.bounces += 1
            self.hoop_bounces += 1
        
        ball_pos = pygame.math.Vector2(self.rect.centerx, self.rect.centery)
        
        hoop_distance = (self.hoop_coords[self.scored_side] - ball_pos).magnitude()
        if hoop_distance > 45:
            return
        
        self.scored()
        
    def handle_shooting(self, dt):
        
        if self.height != 0:
            self.velocity += self.gravity * dt
            self.height += self.velocity * dt
            if self.height < -250 * self.scale_factor:
                self.ceiling = 350
                self.height = -250 * self.scale_factor
                self.velocity *= -.67
                self.bounces += 1
                if self.bounces >= 1:
                    self.rebound()
            
        self.hoop_detection(dt, left_side=True)
        self.hoop_detection(dt)
        
        
    def handle_catch(self):
        colliding_sprites = pygame.sprite.spritecollide(
            self, self.group, False, pygame.sprite.collide_mask
        )
        colliding_sprites = [
            sprite
            for sprite in colliding_sprites
            if sprite != self and sprite != self.player
            and (isinstance(sprite, (OppBots, TeamBots)))
        ]
        
        if colliding_sprites:
            return self.catch(colliding_sprites)
        
    def handle_bounds(self):
        if self.rect.right > 2000:
            self.rect.right = 2000
            
        if self.rect.left < 10:
            self.rect.left = 10
            self.direction.x *= -0.67
            
        if self.rect.top < self.ceiling:
            self.rect.top = self.ceiling
            self.direction.y *= -0.67
            self.velocity *= -0.67
        
        if self.rect.bottom > 850:
            self.rect.bottom = 850
            self.direction.y *= -0.67
            self.velocity *= -0.67

    def update(self, dt):
        self.last_pos = self.pos.copy()
        self.pos += self.direction * self.speed * dt * self.shootpower
        self.rect.topleft = (round(self.pos.x), round(self.pos.y))
        self.rect.center = round(self.pos.x), round(self.pos.y - self.height)
        
        self.scale()
        
        self.handle_bounds()
        
        if self.shooting:
            self.handle_shooting(dt)
        else:
            self.handle_catch()


#
