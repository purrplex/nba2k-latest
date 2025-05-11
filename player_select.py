import pygame


class PlayerSelect(pygame.sprite.Sprite):
    def __init__(self, pos, groups, team, player):
        super().__init__(groups)

        # Jumping & Gravity
        self.gravity = 1200
        self.jump_power = -400
        self.velocity_y = 0
        self.is_jumping = False

        self.team = team
        self.current_player = player

        self.selected_player = None
        self.was_selected = True

        self.speed = 200
        self.max_speed = 500
        self.min_speed = 200
        self.speed_decay = 100

        self.dt = 0

        self.import_assets()
        self.frame_index = 0
        self.image = self.idle_animation[self.frame_index]
        self.rect = self.image.get_rect(center=pos)
        self.pos = pygame.math.Vector2(self.rect.center)

        self.direction = pygame.math.Vector2(0, 0)

    def import_assets(self):

        self.idle_animation = [
            pygame.transform.scale(
                pygame.image.load(
                    f"images/{self.team}/{self.current_player}/{self.current_player}_idle/{frame}.png"
                ).convert_alpha(),
                (400, 400),
            )
            for frame in range(10)
        ]
        self.animation = self.idle_animation

    def apply_gravity(self):
        self.velocity_y += self.gravity * self.dt
        self.pos.y += self.velocity_y * self.dt

        if self.pos.y >= 400:
            self.pos.y = 400
            self.velocity_y = 0
            self.is_jumping = False

    def move(self):
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        # Gradually decrease speed
        if self.speed > self.min_speed:
            self.speed -= self.speed_decay * self.dt

        # Update position
        self.pos += self.direction * self.speed * self.dt
        self.rect.center = round(self.pos.x), round(self.pos.y)

        if self.selected_player == self.current_player:
            if not self.was_selected:
                self.was_selected = False
                if not self.is_jumping and self.jumping_inc == 0:
                    self.velocity_y = self.jump_power
                    self.is_jumping = True
                    self.jumping_inc = 1
                    self.animation = self.idle_animation
                    self.frame_index = 0
        else:
            self.was_selected = False
            self.jumping_inc = 0
            self.is_jumping = False

    def animate(self):
        # Loop idle animation
        self.frame_index += 10 * self.dt
        if self.frame_index >= len(self.idle_animation):
            self.frame_index = 0

        self.image = self.idle_animation[int(self.frame_index)]

    def update(self, selected_player, dt):
        self.dt = dt

        if self.selected_player != selected_player:
            self.selected_player = selected_player
            self.import_assets()

        self.apply_gravity()
        self.animate()
        self.move()
