import pygame, sys
import time
import random

def game_loop(self):
	self.tipoff_music.stop()
	self.game_music.play(loops=-1)
	while True:

		events = pygame.event.get()
		for event in events:
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()

		dt = self.clock.tick(60) / 1000

		if self.team == "knicks" or self.team == None:
			self.screen.blit(self.knicksbackground, (-492, 0))
			self.background = self.knicksbackground
		elif self.team == "lakers":
			self.screen.blit(self.lakersbackground, (-492, 0))
			self.background = self.lakersbackground

		self.qtr = self.show_qtr(self.qtr, self.screen)

		self.show_score()

		if self.inbounder_is_active:
			(
				self.inbounder_is_active,
				self.snap,
				self.outOfBounds,
			) = self.inbounder.update(
				dt,
				events,
				self.outOfBounds,
			)

			self.inbounder.snap_throw_instructions(self.screen)

			colliding_sprites = self.testball.update() + self.testball2.update()

		else:

			self.spawn_team_bots()
			self.spawn_opp_bots()


			(
				self.inbounder_is_active,
				self.snap,
				self.outOfBounds,
			) = self.inbounder.update(
				dt,
				events,
				self.outOfBounds,
			)

			self.all_sprites_group.customize_draw(
				self.player,
				self.screen,
				self.background,
				self.qtr,
				self.show_qtr,
				self.show_score,      

			)
			if self.player.passselecting == True:
				self.show_passselectionscreen(events)

			else:
				free_throw = False
				for bot in self.bots_group:
					__, flop = bot.update(dt, self.screen, time, self.winner)
					if flop:
						free_throw = True

				colliding_sprites = self.testball.update() + self.testball2.update()
				for sprite in colliding_sprites:
					if sprite == self.player:
						self.player.give_ball()

				self.outOfBounds, flop, fall = self.player.update(
					dt,
					events,
					self.screen,
					self.team,
					self.winner,
					self.selected_player,
				)

				if flop or fall or free_throw:
					self.free_throw = True
					if self.offensiveplay:
						self.free_throw_shooter = self.player
					else:
						self.free_throw_shooter = "kobe"
					self.FreeThrow.start(self.screen, self.player)
					self.free_throw = False

					# if self.offensiveplay == True:
					# 	self.free_throw = True
					# 	self.free_throw_shooter = self.player
					# 	self.FreeThrow.start(self.screen, self.player)
					# 	self.free_throw = False
					# else: 
					# 	chance = random.randint(0,20)
					# 	print(chance)
					# 	if chance == 19:
					# 		self.offensiveplay = True
					# 		self.deffensiveplay = False

		if self.basketball:
			self.basketball.update(dt)
			
		self.show_niceshot(dt)

		if self.outOfBounds:
			self.ball = False
			self.snap = False
			self.qtr += 1

			 

		pygame.display.update()


