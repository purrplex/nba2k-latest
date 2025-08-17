import pygame
import random
from pygame.math import Vector2 as vector
from stats import PLAYER_STATS


class OppBots(pygame.sprite.Sprite):

	def __init__(self, pos, groups, player, team, selected_player, outOfBounds, create_basketball):
		super().__init__(groups)
		self.group = groups
		self.player = player
		self.team = team
		self.selected_player = selected_player
		self.WINDOW_WIDTH, self.WINDOW_HEIGHT = 1215, 812
		self.winner = None
		self.status = "right"
		self.frame_index = 0
		self.direction = vector(1, 0)
		self.position = vector(pos)
		self.rect = None
		self.outOfBounds = outOfBounds
		self.create_basketball = create_basketball


		self.import_assets()
		self.animation = self.animations["idle"]
		self.image = self.animation[self.frame_index]
		self.rect = self.image.get_rect(center=pos)
		self.hoop = {}
		self.hoop['knicks'] = pygame.math.Vector2(1850,562)
		self.hoop['lakers'] = pygame.math.Vector2(310,562)
		
		if selected_player in PLAYER_STATS:
			self.stats = PLAYER_STATS[selected_player]
		else:
			self.stats = {
				'shoot_chance':50,
			}

		self.height = 0
		self.velocity = 0
		self.jump_speed = 400
		self.jump_start = 1
		self.gravity = -800

		self.speed = 200
		self.max_speed = 500
		self.min_speed = 200
		self.speed_decay = 100
		self.steal_timer = pygame.time.get_ticks()

		self.stop = 0
		self.ball = None
		self.steal = False
		self.pass_steal = False
		self.stealing = False
		self.landing = None
		self.flopping = False
		self.flopped = False
		self.falling = False
		self.before_jump = None
		self.is_idle = False
		self.free_throw = False
		self.basketball = None
		self.scale_factor = 1.0

		self.notice_radius = 1000
		self.move_radius = 350
		self.guard_radius = 120
		
		self.delay_move_timer = 0
		self.delay_move = False
		self.delay = 0.2

		self.jump_sound = pygame.mixer.Sound("images/sounds/jump.wav")
		self.jump_sound.set_volume(0.05)

		self.landing_sound = pygame.mixer.Sound("images/sounds/land.ogg")
		self.landing_sound.set_volume(0.02)

	def load_animation(self, path, frame_count):
		images = []

		for i in range(frame_count):
			image_path = f"{path}{i}.png"
			image = pygame.image.load(image_path).convert_alpha()

			images.append(image)

		return images

	def import_assets(self):
		# Define animation types and frame counts
		animation_data = {
			"run_right": ("run/", 8),
			"run_left": ("run_left/", 8),
			"jump": ("jump/", 9),
			"jump_left": ("jump_left/", 9),
			"land_right": ("land/", 7),
			"land_left": ("land_left/", 7),
			"idle": ("idle/", 10),
			"idle_left": ("idle_left/", 10),
			"dribble_right": ("dribble/", 8),
			"dribble_left": ("dribble_left/", 8),
			"shoot": ("shoot/", 6),
			"shoot_left": ("shoot_left/", 6),
			"pass": ("pass/", 7),
			"pass_left": ("pass_left/", 7),
			"steal": ("steal/", 8),
			"steal_left": ("steal_left/", 8),
			"flop": ("flop/", 8),
			"flop_left": ("flop_left/", 8),
			"fall": ("fall/", 12),
			"fall_left": ("fall_left/", 12),
		}

		# Determine which player's animations to load
		if self.winner:
			if self.team == "knicks":
				team = "lakers"
				player = self.selected_player
			else:
				team = "knicks"
				player = self.selected_player
		else:
			if self.team == "lakers":
				team = "knicks"
				player = self.selected_player
			else:
				team = "lakers"
				player = self.selected_player

		"""if self.selected_player:
			team = "lakers"
			player = self.selected_player"""

		# Generate the base path dynamically
		base_path = f"images/{team}/{player}/{player}_"

		# Load animations dynamically
		self.animations = {
			key: self.load_animation(base_path + path, frames)
			for key, (path, frames) in animation_data.items()
		}

	def outofbounds(self, screen, time):
		screen.fill((0, 0, 0))
		my_font = pygame.font.Font("images/font.ttf", 100)

		message = "OUT OF BOUNDS"
		color = "red"

		downs_surface = my_font.render(message, True, color)
		downs_rect = downs_surface.get_rect(
			center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 2)
		)
		screen.blit(downs_surface, downs_rect)
		pygame.display.flip()
		time.sleep(1)

		self.speed = 0
		self.outOfBounds = True
		self.direction = vector(1, 0)
		self.player = None

	def reset_position(self, x=250, y=450):
		self.status = "right"
		self.speed = 0
		self.position = vector(x, y)
		self.rect.center = round(self.position.x), round(self.position.y)

	def free_throw_init(self, x, y, shooter):
		self.reset_position(x, y)
		self.is_idle = True
		self.free_throw = True
		self.direction.x = 0
		self.direction.y = 0

		# if self.offensiveplay:
		# 	self.status = "right"
		# if self.deffensiveplay:
		# 	self.status = "left"
		
		self.direction = pygame.math.Vector2(0,0)
		
		if self == shooter:
			self.ball = True
			self.status = "left"
		else:
			self.ball = False

	def free_throw_exit(self):
		self.free_throw = False
		self.position = self.player.position.copy()
		self.position.x += 120

	def shoot(self):
		if self.free_throw:
			self.ball = True
			 
		self.jump_sound.play()
		self.velocity = self.jump_speed
		self.height = self.jump_start
		self.basketball_created = False
		self.frame_index = 0
		self.direction = pygame.math.Vector2(0, 0)


	def shoot_miss(self):
		if self.free_throw:
			self.ball = True

		self.jump_sound.play()
		self.velocity = self.jump_speed
		self.height = self.jump_start
		self.basketball_created = False
		self.frame_index = 0
		self.direction = pygame.math.Vector2(0, 0)

	def get_player_distance_direction(self):
		enemy_pos = vector(self.rect.center)
		player_pos = vector(self.player.rect.center)
		"""print("enemy_pos", enemy_pos)
		print("player_pos", player_pos)"""
		distance = (player_pos - enemy_pos).magnitude()

		if distance != 0:
			direction = (player_pos - enemy_pos).normalize()
		else:
			direction = vector()

		return (distance, direction)

	def face_player(self):
		distance, direction = self.get_player_distance_direction()

		if distance < self.notice_radius:
			if -0.95 < direction.y < 0.95:
				if direction.x < 0:  # player to the left
					self.direction.x = -1
					self.status = "left"
				elif direction.x > 0:  # player to the right
					self.direction.x = 1
					self.status = "right"		
			
		if self.ball == True:
			self.status = "left"

	def move_to_player(self):
		distance, direction = self.get_player_distance_direction()
		if self.guard_radius < distance < self.move_radius:
			self.is_idle = False
			self.direction = direction
			self.speed += 1
		else:
			self.is_idle = True
			self.speed = 0
			self.direction = vector(0, 0)
			self.delay_move = True
			self.delay_move_timer = 0

	def move(self, dt, screen, time):
		if self.direction.magnitude() != 0:
			self.direction = self.direction.normalize()

		if self.delay_move:
			self.delay_move_timer += dt
			if self.delay_move_timer > self.delay:
				self.delay = random.random()*0.1 + 0.1
				self.delay_move_timer = 0
				self.delay_move = False
		elif not self.free_throw:
			self.face_player()
			self.move_to_player()

		# Gradually decrease speed
		if self.speed > self.min_speed:
			self.speed -= self.speed_decay * dt

		# Update position
		self.position += self.direction * self.speed * dt
		if self.height != 0:
			self.velocity += self.gravity * dt
			self.height += self.velocity * dt

			if self.height < 0:
				self.height = 0
				self.velocity = 0
				self.frame_index = 0
				self.landing = True
				self.stop = 0

		self.rect.center = round(self.position.x), round(self.position.y - self.height)

		self.scale_factor = max(1.0, min(1.5, 1 + (self.position.y - 400) / 500))

		self.speed = max(self.min_speed, min(self.speed, self.max_speed))

		if self.landing:
			self.ball = False
			self.pass_steal = False

		if self.position.x < 20:
			self.position.x = 20

		"""if self.position.x > 2000 and not self.height != 0:
			self.outofbounds(screen, time)
			self.reset_position()
			self.direction.y = 0
 pygame.time.get_ticks()¶
		if (self.position.y < 350 or self.position.y > 775) and not self.height != 0:
			self.outofbounds(screen, time)
			self.reset_position()
			self.direction.y = 0"""

	def draw(self, screen):
		screen.blit(self.image, self.rect)
		
	def opp_steal(self):
		if self.free_throw:
			return
		st_elapsed = pygame.time.get_ticks() - self.steal_timer
		if st_elapsed == 0:
			self.steal = False
		if  st_elapsed >= 5000:
			if random.random() < 0.1:
				self.steal = True
			else:
				self.steal = False
			self.steal_timer = pygame.time.get_ticks()

	def animation_done(self):
		if self.steal:
			self.steal = False
			if self.player.ball:
				self.player.ball = False
				self.ball = True

		if self.flopping:
			self.flopped = True
				
		self.frame_index = len(self.animation) - 1
		
		if self.stop == 0:
			self.stop += 1

		if self.ball:
			self.speed = 0
		self.pass_steal = False
		self.landing = False
		self.flopping = False
		self.falling = False


	def animate(self, dt):
		if self.height != 0:
			if self.ball:

				if self.status == "right":
					self.animation = self.animations["shoot"]
				elif self.status == "left":
					self.animation = self.animations["shoot_left"]
			else:
				if self.status == "right":
					self.animation = self.animations["jump"]
				elif self.status == "left":
					self.animation = self.animations["jump_left"]
		else:
			if self.ball:
				if self.status == "right":
					if self.landing:
						self.is_idle = False
						self.animation = self.animations["land_right"]
					else:
						self.animation = self.animations["dribble_right"]
						self.direction.x = 1
					if self.pass_steal:
						self.animation = self.animations["pass"]
				elif self.status == "left":
					if self.landing:
						self.is_idle = False
						self.animation = self.animations["land_left"]
					else:
						self.animation = self.animations["dribble_left"]
						self.direction.x = -1
					if self.pass_steal:
						self.animation = self.animations["pass_left"]
			else:
				if self.status == "right":
					self.animation = self.animations["run_right"]
					self.direction.x = 1
					if self.landing:
						self.is_idle = False
						self.animation = self.animations["land_right"]
					if self.is_idle:
						self.animation = self.animations["idle"]
						self.direction.x = 0

					if self.steal:
						self.animation = self.animations["steal"]

					if self.flopping:
						self.animation = self.animations["flop"]

					if self.falling:
						self.animation = self.animations["fall"]

				elif self.status == "left":
					self.animation = self.animations["run_left"]
					self.direction.x = -1

					if self.landing:
						self.is_idle = False
						self.animation = self.animations["land_left"]

					if self.is_idle:
						self.animation = self.animations["idle_left"]
						self.direction.x = 0

					if self.steal:
						self.animation = self.animations["steal_left"]

					if self.flopping:
						self.animation = self.animations["flop_left"]

					if self.falling:
						self.animation = self.animations["fall_left"]

		if self.landing:
			self.frame_index += 15 * dt
		else:
			self.frame_index += 10 * dt

		if self.animation in [
			self.animations["jump"],
			self.animations["jump_left"],
			self.animations["shoot"],
			self.animations["shoot_left"],
			self.animations["pass"],
			self.animations["pass_left"],
			self.animations["land_right"],
			self.animations["land_left"],
			self.animations["steal"],
			self.animations["steal_left"],
			self.animations["flop"],
			self.animations["flop_left"],
			self.animations["fall"],
			self.animations["fall_left"],
		]:

			if self.frame_index > len(self.animation) - 2:
				self.animation_done()
			else:
				#self.steal = True
				if self.ball or self.landing or self.steal:
					self.speed = 0
				else:
					self.speed = self.speed

		if self.frame_index >= len(self.animation):
			self.frame_index = 0
		self.image = self.animation[int(self.frame_index)]

		# Applys the scale factor to the image
		width, height = self.image.get_size()
		new_width = int(width * self.scale_factor)
		new_height = int(height * self.scale_factor)
		self.image = pygame.transform.scale(
			self.animation[int(self.frame_index)], (new_width, new_height)
		)
		self.rect = self.image.get_rect(center=self.rect.center)

	def release_ball(self, action, target=None):
		shootpower = abs(self.position.x - self.WINDOW_WIDTH/2)
		shootpower = 1 - (shootpower/self.WINDOW_WIDTH/2)
		shootpower = shootpower**4*4
		shootpower += random.random()*0.5
		ball_data = {
			'player':self,
			'shootpower':shootpower,
			'action':action
		}
		
		if self.status == "right":
			ball_data['pos'] = (self.rect.topright[0] - 50, self.rect.topright[1] + 10)
			ball_data['direction'] = (self.hoop['knicks'] - self.position).normalize()
		elif self.status == "left":
			ball_data['pos'] = (self.rect.topleft[0] + 50, self.rect.topleft[1] + 10)
			ball_data['direction'] = (self.hoop['lakers'] - self.position).normalize()
			
		self.create_basketball(ball_data)
		self.basketball_created = True
		self.ball = False
		
	def deffensive_position(self):
		self.status = "left"
		self.speed = 0
		self.position = self.player.position.copy()	
		self.position.x -= 120	
		self.rect.center = round(self.position.x), round(self.position.y)	

	def offensive_position(self):
		self.status = "right"
		self.speed = 0
		self.position = self.player.position.copy()
		self.position.x += 120
		self.rect.center = round(self.position.x), round(self.position.y)
		
	def give_ball(self):
		self.ball = True
		self.basketball_created = False

	def update_basketball(self, dt):
		if not self.ball or self.basketball_created:
			return
		
		if self.height == 0:
			if random.random() > .996:
				self.velocity = self.jump_speed
				self.height = self.jump_start
		
		if self.height != 0:
			if self.frame_index == len(self.animation) - 1:
				self.release_ball("shoot")

	def update(self, dt, screen, time, winner):
		self.winner = winner
		self.outOfBounds = True
		self.move(dt, screen, time)
		self.update_basketball(dt)
		self.animate(dt)
		self.opp_steal()
		

		if self.free_throw:
			self.direction.x = 0
			self.direction.y = 0

		return (self.outOfBounds, self.flopped)

