import pygame
import random
from pygame.math import Vector2 as vector
from stats import PLAYER_STATS


class TeamBots(pygame.sprite.Sprite):

	def __init__(
		self,
		pos,
		groups,
		player,
		team,
		selected_player,
		play_name,
		outOfBounds,
		target_pos,
		create_basketball
	):
		super().__init__(groups)
		self.group = groups
		self.player = player
		self.team = team
		self.create_basketball = create_basketball
		self.play_name = play_name
		self.selected_player = selected_player
		self.WINDOW_WIDTH, self.WINDOW_HEIGHT = 1215, 812
		self.winner = None
		self.status = "right"
		self.frame_index = 0
		self.direction = vector(1, 0)

		self.rect = None
		self.outOfBounds = outOfBounds
		self.play = None

		self.import_assets()
		self.animation = self.animations["idle"]
		self.image = self.animation[self.frame_index]
		self.rect = self.image.get_rect(center=pos)

		self.position = vector(self.rect.center)
		self.target_pos = target_pos
		self.target_position = vector(self.target_pos[0])
		
		if selected_player in PLAYER_STATS:
			self.stats = PLAYER_STATS[selected_player]
		else:
			self.stats = {
				"shoot_chance":50,
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

		self.love = True
		self.deffensive = None
		self.stop = 0
		self.ball = None
		self.pass_steal = False
		self.stealing = False
		self.passing = False
		self.landing = None
		self.flopping = False
		self.flopped = False
		self.falling = False
		self.before_jump = None
		self.is_idle = False
		self.free_throw = False
		self.basketball = None
		self.basketball_created = False
		self.scale_factor = 1.0
		self.hoop = {}
		self.hoop['knicks'] = pygame.math.Vector2(1850,562)
		self.hoop['lakers'] = pygame.math.Vector2(310,562)

		self.notice_radius = 1000
		self.move_radius = 850
		self.guard_radius = 10

		self.last_move_time = pygame.time.get_ticks()

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
				team = "knicks"
				player = self.selected_player
			else:
				team = "lakers"
				player = self.selected_player
		else:
			if self.team == "lakers":
				team = "lakers"
				player = self.selected_player
			else:
				team = "knicks"
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

	def deffensive_position(self):
		self.status = "left"
		self.speed = 0
		pos = random.choice(self.target_pos)
		self.position = pygame.math.Vector2(pos[0]-850, pos[1])
		self.rect.center = round(self.position.x), round(self.position.y)
		self.deffensive = True

	def offensive_position(self):
		self.deffensive = False
		self.status = "right"
		self.speed = 0
		pos = random.choice(self.target_pos)
		self.position = pygame.math.Vector2(pos[0], pos[1])
		self.rect.center = round(self.position.x), round(self.position.y)


	def free_throw_init(self, x, y, shooter):
		self.reset_position(x, y)
		self.is_idle = True
		self.free_throw = True
		self.direction.x = 0
		self.direction.y = 0

		if self == shooter:
			self.ball = True
		else:
			self.ball = False

	def free_throw_exit(self):
		self.free_throw = False
		position = random.choice(self.target_pos)
		self.position = vector(position[0], position[1])

	def get_position_distance_direction(self):
		# Change target every 2 seconds
		current_time = pygame.time.get_ticks()
		if current_time - self.last_move_time > 2000:
			self.target_position = random.choice(self.target_pos)
			if self.deffensive:
				self.target_position = (self.target_position[0]-850, self.target_position[1])
			self.last_move_time = current_time

		distance = (self.target_position - self.position).magnitude()

		if distance != 0:
			direction = (self.target_position - self.position).normalize()
		else:
			direction = vector()

		return (distance, direction)

	def get_player_distance_direction(self):
		enemy_pos = vector(self.rect.center)
		player_pos = vector(self.player.rect.center)
		distance = (player_pos - enemy_pos).magnitude()

		if distance != 0:
			direction = (player_pos - enemy_pos).normalize()
		else:
			direction = vector()

		return (distance, direction)

	def face_player(self):
		distance, direction = self.get_player_distance_direction()
		if not self.ball or self.basketball_created:
			if distance < self.notice_radius:
				if -0.95 < direction.y < 0.95:
					if direction.x < 0:  # player to the left
						self.direction.x = -1
						self.status = "left"
					elif direction.x > 0:  # player to the right
						self.direction.x = 1
						self.status = "right"
		if self.ball == True:
			self.status = "right"

	def move_to_position(self):
		"""self.is_idle = True
		self.speed = 0
		self.direction = vector(0, 0)"""

		distance, direction = self.get_position_distance_direction()

		if self.guard_radius < distance < self.move_radius:
			
			self.is_idle = False
			self.direction = direction
			self.speed += 1
		else:
			self.is_idle = True
			self.speed = 0
			self.direction = vector(0, 0)

	def move(self, dt, screen, time):
		if self.direction.magnitude() != 0:
			self.direction = self.direction.normalize()

		if not self.free_throw and not self.ball:
			self.face_player()
			self.move_to_position()
		elif self.ball:
			self.move_to_position()
			self.status = "right"

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

		if (self.position.y < 350 or self.position.y > 775) and not self.height != 0:
			self.outofbounds(screen, time)
			self.reset_position()
			self.direction.y = 0"""

	def draw(self, screen):
		screen.blit(self.image, self.rect)
		
	def animation_done(self):
		self.frame_index = len(self.animation) - 1

		if self.stop == 0:
			self.stop += 1

		if self.flopping:
			self.flopped = True

		if self.ball:
			self.speed = 0
		self.pass_steal = False
		self.landing = False
		self.flopping = False
		self.falling = False

	def animate(self, dt):
		if self.height != 0:
			if self.ball or self.basketball_created:
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

					if self.pass_steal:
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

					if self.pass_steal:
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
				self.pass_steal = True
				if self.ball or self.landing or self.pass_steal:
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
			
			
			
		if action == "pass":
			if target:
				ball_data['direction'] = (self.bot.position - self.position).normalize()
			
		
		self.create_basketball(ball_data)
		self.basketball_created = True

	def update_ball_state(self):
		self.height = 0
		self.velocity = 0
		self.direction = pygame.math.Vector2(0,0)
		self.frame_index = 0
		self.speed = 0
		self.steal = False
		self.passing = False
		
	def give_ball(self):
		self.ball = True
		self.basketball_created = False
		self.update_ball_state()

	def take_ball(self):
		self.ball = False
		self.basketball_created = False
		self.update_ball_state()

	def update_basketball(self, dt):
		if not self.ball or self.basketball_created:
			return
		
		if self.height == 0:
			if random.random() > .99:
				self.velocity = self.jump_speed
				self.height = self.jump_start
		
		if self.height != 0:
			if self.frame_index == len(self.animation) - 1:
				self.release_ball("shoot")
		elif self.passing:
			if self.frame_index == len(self.animation) - 1:
				self.release_ball("pass")
				self.passing = False
		

	def update(self, dt, screen, time, winner):
		self.winner = winner
		self.outOfBounds = True
		self.move(dt, screen, time)
		self.update_basketball(dt)
		self.flopped = False
		self.animate(dt)

		if self.free_throw:
			self.direction.x = 0
			self.direction.y = 0

		return (self.outOfBounds, self.flopped)

