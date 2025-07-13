import pygame
import time
import random
from basketball import Basketball


class Player(pygame.sprite.Sprite):
	def __init__(self, pos, groups, create_basketball):
		super().__init__(groups)
		self.group = groups
		self.WINDOW_WIDTH, self.WINDOW_HEIGHT = 1215, 812
		self.winner = None
		self.team = None
		self.status = "right"
		self.frame_index = 0
		self.direction = pygame.math.Vector2(1, 0)
		self.position = pygame.math.Vector2(pos)
		self.rect = None
		self.selected_player = "brunson"
		self.dttimer = 0
		self.shootpower = 1
		self.import_assets()
		self.animation = self.animations["idle"]
		self.image = self.animation[self.frame_index]
		self.rect = self.image.get_rect(center=pos)
		self.create_basketball = create_basketball
		

		self.height = 0
		self.velocity = 0
		self.jump_speed = 400
		self.jump_start = 1
		self.gravity = -800

		self.speed = 200
		self.max_speed = 500
		self.min_speed = 200
		self.speed_decay = 100
		
		self.shooting = False
		self.shoottimer = False
		self.ball = None
		self.pass_steal = False
		self.passing = False
		self.passselecting = None
		self.steal = False
		self.stealing = False
		self.landing = None
		self.flopping = False
		self.flopped = False
		self.falling = False
		self.fall = False
		self.before_jump = None
		self.is_idle = False
		self.free_throw = False
		self.basketball = None
		self.team_bots = None
		self.bot = None
		self.basketball_created = False
		self.player_moves_with_ball = True
		self.scale_factor = 1.0
		self.hoop = {}
		self.hoop['knicks'] = pygame.math.Vector2(1850,562)
		self.hoop['lakers'] = pygame.math.Vector2(310,562)

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
				player = self.selected_playerteam_ball
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

		if not self.selected_player:
			team = "knicks"
			player = "brunson"

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
		self.direction = pygame.math.Vector2(1, 0)

	def offensiveplay_screen(self, screen):
		screen.fill((0, 0, 0))
		my_font = pygame.font.Font("images/font.ttf", 100)

		message = "OFFENSIVE PLAY"
		color = "yellow"

		downs_surface = my_font.render(message, True, color)
		downs_rect = downs_surface.get_rect(
			center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 2)
		)
		screen.blit(downs_surface, downs_rect)
		pygame.display.flip()
		time.sleep(1)

		self.direction = pygame.math.Vector2(1, 0)

	def deffensiveplay_screen(self, screen):
		screen.fill((0, 0, 0))
		my_font = pygame.font.Font("images/font.ttf", 100)

		message = "DEFFENSIVE PLAY"
		color = "yellow"

		downs_surface = my_font.render(message, True, color)
		downs_rect = downs_surface.get_rect(
			center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 2)
		)
		screen.blit(downs_surface, downs_rect)
		pygame.display.flip()
		time.sleep(1)

		self.direction = pygame.math.Vector2(1, 0)

	def reset_position(self, x=1100, y=500):
		self.status = "right"
		self.speed = 0
		self.position = pygame.math.Vector2(x, y)
		self.rect.center = round(self.position.x), round(self.position.y)

	def free_throw_init(self, x, y, shooter):
		self.reset_position(x, y)
		self.free_throw = True
		self.is_idle = True
		self.direction.x = 0
		self.direction.y = 0

		if self == shooter:
			self.ball = True
		else:
			self.ball = False

	def free_throw_exit(self):
		self.free_throw = False

	def move(self, dt, screen):
		if self.direction.magnitude() != 0:
			self.direction = self.direction.normalize()

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

		self.rect.center = round(self.position.x), round(self.position.y - self.height)

		self.scale_factor = max(1.0, min(1.5, 1 + (self.position.y - 400) / 500))

		self.speed = max(self.min_speed, min(self.speed, self.max_speed))

		if self.landing:
			self.passing = False
			self.steal = False

		if self.position.x < 20:
			self.position.x = 20

		if self.position.x > 2000 and not self.height != 0:
			print('what')
			self.outofbounds(screen, time)
			self.reset_position()
			self.direction.y = 0

		if (self.position.y < 350 or self.position.y > 775) and not self.height != 0:
			print(self.position.y)
			self.outofbounds(screen, time)
			self.reset_position()
			self.direction.y = 0

	def draw(self, screen):
		screen.blit(self.image, self.rect)

	def input(self, events, dt):
		for event in events:
			if event.type == pygame.KEYUP:
				if event.key == pygame.K_w and self.height == 0:    
					self.jump_sound.play()
					self.velocity = self.jump_speed
					self.height = self.jump_start
					self.animation = self.animation
					self.basketball_created = False
					self.frame_index = 0
					self.direction = pygame.math.Vector2(0, 0)
					power = min(self.dttimer, 2.5) / 2.5
					self.shootpower = power * 5
					self.dttimer = 0
					self.shoottimer = False
					# self.shooting = False
					
			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE:
					self.speed += 50

				if event.key == pygame.K_w and self.height == 0:
					self.shoottimer = True   
					self.shooting = True    

				if event.key == pygame.K_d and not self.passing and self.ball:
					self.passing = True
					self.frame_index = 0
					self.passselecting = True
					
				elif event.key == pygame.K_d and not self.steal and not self.ball:
					self.steal = True
					self.frame_index = 0

				if event.key == pygame.K_a and not self.flopping and not self.ball:
					self.flopping = True
					self.frame_index = 0

				if event.key == pygame.K_s and not self.falling and not self.ball:
					self.falling = True
					self.frame_index = 0

		keys = pygame.key.get_pressed()
		if self.shoottimer == True:
			self.dttimer += dt    

		if self.free_throw or not self.player_moves_with_ball:
			self.is_idle = True
			self.direction.x = 0
			self.direction.y = 0
		
		if not self.ball:
			# Reset direction
			self.is_idle = True
			self.direction.x = 0
			self.direction.y = 0

			# Horizontal movement
			if keys[pygame.K_RIGHT]:
				self.is_idle = False
				self.status = "right"
				self.direction.x = 1
			elif keys[pygame.K_LEFT]:
				self.is_idle = False
				self.status = "left"
				self.direction.x = -1

			# Vertical movement
			if keys[pygame.K_UP]:
				self.is_idle = False
				self.direction.y = -1
			if keys[pygame.K_DOWN]:
				self.is_idle = False
				self.direction.y = 1
		else:
			if not self.passing and not self.steal:
				if keys[pygame.K_RIGHT]:
					self.status = "right"
					self.direction.x = 1
				elif keys[pygame.K_LEFT]:
					self.status = "left"
					self.direction.x = -1

				# Vertical movement
				if keys[pygame.K_UP]:
					self.direction.y = -1
				if keys[pygame.K_DOWN]:
					self.direction.y = 1
					
	def animation_done(self):
		self.frame_index = len(self.animation) - 1
		if self.ball and not self.basketball_created:
			self.speed = 0
			if self.height != 0:
				self.release_ball("shoot")
			elif self.passing:
				self.release_ball("pass")
				self.passing = False
			self.basketball_created = True
			self.ball = False
		elif self.steal:
			pass

		if self.flopping:
			self.flopped = True

		if self.falling:
			self.fall = True

		self.steal = False
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
					if self.passing:
						self.animation = self.animations["pass"]
				elif self.status == "left":
					if self.landing:
						self.is_idle = False
						self.animation = self.animations["land_left"]
					else:
						self.animation = self.animations["dribble_left"]
						self.direction.x = -1
					if self.passing:
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
				if self.ball or self.landing or self.passing or self.steal:
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

	def draw_speed_meter(self, screen):
		bar_width = 200
		bar_height = 20
		bar_x = 170
		bar_y = 20
		pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height))

		# Calculate the width of the green bar based on the player's speed 
		green_bar_width = int(
			(self.speed - self.min_speed)
			/ (self.max_speed - self.min_speed)
			* bar_width
		)

		pygame.draw.rect(
			screen, (0, 255, 0), (bar_x, bar_y, green_bar_width, bar_height)
		)
		my_font = pygame.font.Font("images/font.ttf", 50)
		speed_surface = my_font.render("SPEED:", True, pygame.Color(255, 255, 255))
		speed_rect = speed_surface.get_rect()
		speed_rect.midtop = (100, 10)
		screen.blit(speed_surface, speed_rect)
			
			
	def draw_shoot_meter(self, screen):
		bar_width = 200
		bar_height = 20
		bar_x = 170
		bar_y = 50
		pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height))

		# Calculate the width of the green bar based on the player's shot 
		green_bar_width = min(self.dttimer, 2.5) / 2.5 * bar_width
		

		pygame.draw.rect(
			screen, (0, 255, 0), (bar_x, bar_y, green_bar_width, bar_height)
		)
		my_font = pygame.font.Font("images/font.ttf", 50)
		speed_surface = my_font.render("SHOOT:", True, pygame.Color(255, 255, 255))
		speed_rect = speed_surface.get_rect()
		speed_rect.midtop = (100, 30)
		screen.blit(speed_surface, speed_rect)
		
	def release_ball(self, action, target=None):
		ball_data = {
			'player':self,
			'shootpower':self.shootpower,
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
		#self.ball = False
		
	def give_ball(self):
		self.ball = True
		self.basketball_created = False

	def update_basketball(self):
		if not self.ball or self.basketball_created:
			return
		
		if self.frame_index == len(self.animation) - 1:
			self.speed = 0
			if self.height != 0:
				self.release_ball("shoot")
			elif self.passing:
				self.release_ball("pass")
				self.passing = False
			self.basketball_created = True
			self.ball = False
				


	def update(self, dt, events, screen, team, winner, selected_player):
		if (self.team, self.selected_player) != (team, selected_player):
			self.team = team
			self.selected_player = selected_player
			self.import_assets()
			

		if self.shoottimer == True:
			self.draw_shoot_meter(screen)

	
		self.winner = winner
		self.input(events, dt)
		self.outOfBounds = False
		self.move(dt, screen)
		#self.update_basketball()
		self.flopped = False
		self.fall = False
		self.animate(dt)

		return (self.outOfBounds, self.flopped, self.fall)

