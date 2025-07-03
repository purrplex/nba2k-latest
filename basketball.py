import pygame


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
        player = data.get('player')
        super().__init__(player.group[0])

        self.player = player
        self.original_image = pygame.image.load("images/basketball.png").convert_alpha()
        self.image = self.original_image
        self.rect = self.image.get_rect(center=data.get('pos'))
        self.pos = pygame.math.Vector2(self.rect.midleft)
        self.direction = data.get('direction')
        #self.direction.y *= 0.5
        self.shootpower = data.get('shootpower', 1)
        self.point_value = data.get('point_value', 1)
        self.on_score = data.get('score')
        self.on_remove = data.get('remove')
        self.shooting = data.get('action') == "shoot"

        self.group = player.group[0]

        self.speed = 400
        self.menu = False
        self.collision_state = None
        self.backboard_right = pygame.Rect(1900, 210, 1, 100)
        self.hoop_coords = pygame.math.Vector2(1850, 350)
        self.bounces = 0

        self.height = 0
        self.velocity = 0
        self.jump_speed = 400
        self.jump_start = 1
        self.gravity = -800

        self.velocity = self.jump_speed
        self.height = self.jump_start

        self.scale_factor = self.player.scale_factor
        
        self.last_hoop_distance = float('inf')
        
    def remove(self, scored=False):
        self.on_remove(pygame.math.Vector2(self.pos.x, self.pos.y - self.height), scored)
        for group in self.groups():
            group.remove(self)
        return True
        
    def scored(self):
        data = {
            'point_value':self.point_value,
            'player':self.player
        }
        self.on_score(data)
        return self.remove(True)
        
    def scale(self):
        #self.scale_factor = max(1.0, min(1.5, 1 + (self.pos.y - 400) / 500))
        self.scale_factor = (self.pos.y - 462)/213 * 0.5 + 1.5
        width, height = self.original_image.get_size()
        new_width = int(width * self.scale_factor)
        new_height = int(height * self.scale_factor)

        if new_width != self.rect.width or new_height != self.rect.height:
            self.image = pygame.transform.scale(
                self.original_image, (new_width, new_height)
            )
            self.rect = self.image.get_rect(center=self.rect.center)
            
    def hoop_detection(self, dt):
        ball_pos = pygame.math.Vector2(self.rect.centerx, self.rect.centery)
        if (self.hoop_coords.y - ball_pos.y) < 15:
            return
        
        hoop_distance = (self.hoop_coords - ball_pos).magnitude()
        if hoop_distance > 50:
            return

        above_rim = False
        for step in range(10):
            future_ball_pos = ball_pos + self.direction * self.speed * dt * self.shootpower * step
            future_velocity = self.gravity * dt * step
            future_ball_pos.y += future_velocity * dt * step
            future_hoop_distance = (self.hoop_coords - future_ball_pos).magnitude()
            if future_ball_pos.y < self.hoop_coords.y+20:
                above_rim = True
            if abs(future_ball_pos.x - self.hoop_coords.x) < 30:
                if above_rim:
                    return self.scored()


        if abs(ball_pos.x - self.hoop_coords.x) < 12:
            self.pos.x = self.hoop_coords.x
            self.direction.x = 0
            self.direction.y = 0
            return
        
        #if ball_pos.y > self.hoop_coords.y or ball_pos.y < self.hoop_coords.y - 10:
        last_direction = self.direction.copy()
        self.last_hoop_distance = hoop_distance
        direction = (ball_pos - self.hoop_coords).normalize()
        self.direction.x = direction.x
        if direction.x > 0:
            self.direction.x = -0.5
        self.direction.y = 0
        self.pos += self.direction * self.speed * dt * self.shootpower
        self.velocity *= -0.67
        self.velocity += self.gravity * dt
        self.height += self.velocity * dt
        
            
    def handle_shooting(self, dt):
        if not self.shooting:
            return
        
        if self.rect.colliderect(self.backboard_right):
            self.pos.x -= 1
            self.direction.x *= -.67
            self.bounces += 1
            
        if self.height != 0:
            self.velocity += self.gravity * dt
            self.height += self.velocity * dt
            if self.height < -250 * self.scale_factor:
                self.height = -250 * self.scale_factor
                self.velocity = 0
                self.upthescore = True
                self.shooting = False

                return self.remove()
            
        return self.hoop_detection(dt)
        
    def handle_collision(self):
        colliding_sprites = pygame.sprite.spritecollide(
            self, self.group, False, pygame.sprite.collide_mask
        )
        colliding_sprites = [
            sprite
            for sprite in colliding_sprites
            if sprite != self and sprite != self.player
        ]

        if not self.shooting and colliding_sprites:
            return self.remove()

        if self.rect.left > 2100 or self.rect.left < 0 or self.rect.bottom < 0:
            return self.remove()

    def update(self, dt):
        self.pos += self.direction * self.speed * dt * self.shootpower
        self.rect.topleft = (round(self.pos.x), round(self.pos.y))
        self.rect.center = round(self.pos.x), round(self.pos.y - self.height)
               
        if self.handle_shooting(dt):
            return

        self.scale()
        
        self.handle_collision()


