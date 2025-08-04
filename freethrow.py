import pygame, sys
import time
import random

class FreeThrow:

	def __init__(self, game):
		self.game = game

		self.shooter = None

		self.players_set = False

		self.ft_bar = 0



	def draw(self, screen):
		# screen.blit(self.game.background, (-900,0))

		# self.game.player.draw(screen)
		
		# for bot in self.game.team_bots:
			# bot.draw(screen)
		# for bot in self.game.opp_bots:
			# bot.draw(screen)

		# if self.game.basketball:
			# self.game.basketball.draw(screen)

		self.game.all_sprites_group.customize_draw(
				self.game.player,
				screen,
				self.game.background,
				self.game.qtr,
				self.game.show_qtr,
				self.game.show_score,      

			)
			
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
		self.draw_ft_meter(screen)

	def foul_screen(self, screen):
		self.draw_screen(screen, 'FOUL')

	def flop_screen(self, screen):
		self.draw_screen(screen, 'FLOP')


	def setup(self):
		for i, bot in enumerate(self.game.team_bots):

			if self.game.offensiveplay:
				if i < 2:
					bot.free_throw_init((i*120)+1650,(400), self.shooter)
				else:
					bot.free_throw_init(0, 0, self.shooter)

			if self.game.deffensiveplay:
				if i < 2:
					bot.free_throw_init((i*120)+650,(400), self.shooter)
				else:
					bot.free_throw_init(0, 0, self.shooter)

		for i, bot in enumerate(self.game.opp_bots):

			if self.game.offensiveplay:
				if i < 1:
					bot.free_throw_init((i*120)+1750, (600), self.shooter)
				else:
					bot.free_throw_init(0, 0, self.shooter)

			if self.game.deffensiveplay:
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
		self.shooter = shooter
		self.setup()
		if random.randint(0,4):
			self.foul_screen(screen)
			self.free_throw_loop(screen)
		else:
			self.flop_screen(screen)
			self.free_throw_loop(screen)

	def draw_ft_meter(self, screen):
		bar_width = 100
		bar_height = 100
		bar_x = 500
		bar_y = 500
		pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height))

		# Calculate the width of the green bar based on the player's shot 
		green_bar_width = min(self.ft_bar, 100) / 100 * bar_width
		

		pygame.draw.rect(
			screen, (0, 255, 0), (bar_x, bar_y, green_bar_width, bar_height)
		)
		my_font = pygame.font.Font("images/font.ttf", 100)
		speed_surface = my_font.render("FREE THROW POWER:", True, pygame.Color(255, 255, 255))
		speed_rect = speed_surface.get_rect()
		speed_rect.midtop = (bar_x - 100, bar_y)
		screen.blit(speed_surface, speed_rect)		


	def end(self):
		for bot in self.game.bots_group:
			bot.free_throw_exit()

		self.game.player.free_throw_exit()
		
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
		running = True

		# Disable spacebar for a few seconds when the menu is rendered
		self.spacebar_enabled = False
		pygame.time.set_timer(pygame.USEREVENT, 100)

		if not self.game.background:
			if self.game.team == "knicks" or self.game.team == None:
					self.game.background = self.game.knicksbackground
			elif self.game.team == "lakers":
				self.game.background = self.game.lakersbackground

		while running:
			screen.fill((0,0,0))
			events = pygame.event.get()
			for event in events:
				if event.type == pygame.QUIT:
					pygame.quit()
					sys.exit()
				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_SPACE:
						chance = random.randint(10,20)
						self.ft_bar = chance

			decrease_chance = random.randint(15,30)
			if self.ft_bar > 0:
				self.ft_bar -= decrease_chance

			while True:
				self.game.show_free_throw_instructons()
				if pygame.K_s:
					break

				# if event.type == pygame.KEYUP:
				# 	pass

				# if event.type == pygame.KEYDOWN:
				# 	if event.key == pygame.K_ESCAPE:
				# 		self.end()
				# 		return

			
			dt = self.game.clock.tick(60) / 1000

			self.update_players(dt, events, screen)

			if self.game.basketball:
				self.game.basketball.update(dt)

			

			self.draw(screen)
