import pygame, sys
import time
import random

class FreeThrow:

	def __init__(self, game):
		self.game = game

		self.shooter = None

		self.players_set = False


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

	def foul_screen(self, screen):
		self.draw_screen(screen, 'FOUL')

	def flop_screen(self, screen):
		self.draw_screen(screen, 'FLOP')


	def setup(self):
		for i, bot in enumerate(self.game.team_bots[:2]):
			bot.free_throw_init((i*100)+1700, 400, self.shooter)

		for i, bot in enumerate(self.game.opp_bots[:3]):
			bot.free_throw_init((i*100)+1700, 600, self.shooter)

		self.game.player.free_throw_init(1500, 500, self.shooter)

		if self.shooter:
			self.shooter.free_throw_init(1500, 500, self.shooter)

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

				if event.type == pygame.KEYUP:
					pass

				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_ESCAPE:
						self.end()
						return

			dt = self.game.clock.tick(60) / 1000

			self.update_players(dt, events, screen)

			if self.game.basketball:
				self.game.basketball.update(dt)

			self.draw(screen)
