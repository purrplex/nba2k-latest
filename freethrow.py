import pygame, sys
import time
import random

class FreeThrow:

	def __init__(self, game):
		self.game = game
		self.shooter = None
		self.players_set = False
		self.shooter_shot = False
		self.show_instructions = False
		self.running = True

		self.ft_bar = 50

	def draw_instructons_screen(self, screen):
		my_font = pygame.font.Font("images/font.ttf", 100)
		speed_surface = my_font.render("PRESS S TO START", True, "yellow")
		speed_rect = speed_surface.get_rect()
		speed_rect.midtop = (750, 100)
		screen.blit(speed_surface, speed_rect)

	def draw_ft_bar(self, screen):
		if self.ft_bar > 0 and self.ft_bar < 100:
			self.draw_ft_meter(screen)
		elif self.ft_bar <= 0 or self.ft_bar >= 100:
			self.draw_ft_result(screen)
			if self.ft_bar >= 100:
				self.shooter.shoot()
				self.shooter_shot = True
			if self.ft_bar <= 0:
				self.shooter.shoot_miss()
				self.shooter_shot = True

	def draw(self, screen):
		self.game.all_sprites_group.customize_draw(
				self.game.player,
				screen,
				self.game.background,
				self.game.qtr,
				self.game.show_qtr,
				self.game.show_score,

			)

		if not self.shooter_shot:
			self.draw_ft_bar(screen)

		if self.show_instructions:
			screen.fill((0,0,0))
			self.draw_instructons_screen(screen)
			
		pygame.display.flip()

	def draw_screen(self, screen, message):
		screen.fill((0, 0, 0))
		my_font = pygame.font.Font("images/font.ttf", 100)

		color = "yellow"

		downs_surface = my_font.render(message, True, color)
		downs_rect = downs_surface.get_rect(
			center=(self.game.WINDOW_WIDTH // 2, self.game.WINDOW_HEIGHT // 2)
		)
		screen.blit(downs_surface, downs_rect)
		pygame.display.flip()
		time.sleep(1)

	def foul_screen(self, screen):
		self.draw_screen(screen, 'FOUL')

	def flop_screen(self, screen):
		self.draw_screen(screen, 'FLOP')

	def basketball_event(self, event_type):
		self.running = False

	def setup(self):

		if self.game.offensiveplay:

			for i, bot in enumerate(self.game.team_bots):

				if i < 2:
					bot.free_throw_init((i*120)+1650,(400), self.shooter)
				else:
					bot.free_throw_init(0, 0, self.shooter)

		if self.game.deffensiveplay:

			for i, bot in enumerate(self.game.team_bots):

				if i < 2:
					bot.free_throw_init((i*120)+650,(400), self.shooter)
				else:
					bot.free_throw_init(0, 0, self.shooter)

		if self.game.offensiveplay:

			for i, bot in enumerate(self.game.opp_bots):
					
				if i < 1:
					bot.free_throw_init((i*120)+1750, (600), self.shooter)
				else:
					bot.free_throw_init(0, 0, self.shooter)

		if self.game.deffensiveplay:

			for i, bot in enumerate(self.game.opp_bots):
					
				if i < 1:
					bot.free_throw_init((i*120)+750, (600), self.shooter)
				else:
					bot.free_throw_init(0, 0, self.shooter)
		
		if self.game.offensiveplay:
			self.game.player.free_throw_init(1500, 500, self.shooter)
		elif self.game.deffensiveplay:
			self.game.player.free_throw_init(500, 500, self.shooter)

		if self.shooter:
			if self.game.offensiveplay:
				self.shooter.free_throw_init(1500, 500, self.shooter)
			if self.game.deffensiveplay:
				self.shooter.free_throw_init(800, 500, self.shooter)

		self.shooter.ball = False
	
	def start(self, screen, shooter=None):
		self.players_set = False
		self.shooter_shot = False
		self.show_instructions = False
		self.running = True
		self.ft_bar = 50
		
		self.shooter = shooter
		self.setup()
		if random.randint(0,4):
			self.foul_screen(screen)
			self.free_throw_loop(screen)
		else:
			self.flop_screen(screen)
			self.free_throw_loop(screen)

	def draw_ft_meter(self, screen):
		bar_width = 400
		bar_height = 50
		bar_x = 700
		bar_y = 100
		pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height))

		# Calculate the width of the green bar based on the player's shot 
		green_bar_width = min(self.ft_bar, 100)/100 * bar_width
		

		pygame.draw.rect(
			screen, (0, 255, 0), (bar_x, bar_y, green_bar_width, bar_height)
		)
		my_font = pygame.font.Font("images/font.ttf", 70)
		speed_surface = my_font.render("FREE THROW POWER:", True, pygame.Color(255, 255, 255))
		speed_rect = speed_surface.get_rect()
		speed_rect.midtop = (bar_x - 300, bar_y)
		screen.blit(speed_surface, speed_rect)		

	def draw_ft_result(self, screen):
		my_font = pygame.font.Font("images/font.ttf", 70)
		if self.ft_bar <= 0:
			speed_surface = my_font.render("MISS", True, pygame.Color(255, 255, 255))
		if self.ft_bar >= 100:
			speed_surface = my_font.render("NICE SHOT", True, pygame.Color(255, 255, 255))
		speed_rect = speed_surface.get_rect()
		speed_rect.midtop = (400, 100)
		screen.blit(speed_surface, speed_rect)		

	def end(self):
		for bot in self.game.team_bots:
			bot.free_throw_exit()

		for bot in self.game.opp_bots:
			bot.free_throw_exit()

		
	def update_players(self, dt, events, screen):
		for bot in self.game.bots_group:
			bot.update(dt, screen, time, self.game.winner)

		self.game.player.update(
			dt,
			events,
			screen,
			self.game.team,
			self.game.winner,
			self.game.selected_player,
		)
		
	def free_throw_loop(self, screen):
		# Disable spacebar for a few seconds when the menu is rendered
		self.spacebar_enabled = False
		pygame.time.set_timer(pygame.USEREVENT, 100)

		if not self.game.background:
			if self.game.team == "knicks" or self.game.team == None:
					self.game.background = self.game.knicksbackground
			elif self.game.team == "lakers":
				self.game.background = self.game.lakersbackground

		while self.running:
			screen.fill((0,0,0))
			events = pygame.event.get()
			for event in events:
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_SPACE:
						chance = random.randint(10,20)
						self.ft_bar += chance
					if event.key == pygame.K_s:
						self.show_instructions = False
			if self.ft_bar > 0 and self.ft_bar < 100:
				decrease_chance = random.randint(0,5)
				if self.ft_bar > 0 and self.ft_bar < 100:
					self.ft_bar -= decrease_chance

			dt = self.game.clock.tick(60) / 1000

			self.update_players(dt, events, screen)

			if self.game.basketball:
				self.game.basketball.update(dt)
	

			self.draw(screen)
