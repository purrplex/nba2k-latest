import pygame, sys
import time
import random

def game_loop(self):
	self.tipoff_music.stop()
	self.game_music.play(loops=-1)
	while True:
		ball_holder = self.ball_holder
		self.ball_holder_updated = False
		events = pygame.event.get()
		mouse = None
		for event in events:
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			if event.type == pygame.MOUSEBUTTONDOWN:
				mouse = event.pos

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

			# colliding_sprites = self.testball.update() + self.testball2.update()

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
				reach = False
				for bot in self.bots_group:
					__, flop = bot.update(dt, self.screen, time, self.winner)
					if flop:
						free_throw = True

					if bot.ball:
						ball_holder = bot
				# colliding_sprites = self.testball.update() + self.testball2.update()
				# for sprite in colliding_sprites:
					# if sprite == self.player:
						# self.player.give_ball()

				self.outOfBounds, player_action = self.player.update(
					dt,
					events,
					self.screen,
					self.team,
					self.winner,
					self.selected_player,
				)

				if self.player.ball:
					ball_holder = self.player

				if 'block' in player_action:
					block_type = 'FOUL'
					if random.random() > 0.5:
						block_type = 'TURNOVER'

					self.show_text(block_type, self.WINDOW_WIDTH/2, 400, (255,255,0))

				if 'steal' in player_action:
					self.player.offensiveplay_screen(self.screen)
					self.update_play(self.player, show_offense_screen=True)

				if free_throw or player_action in ['flop', 'fall', 'reach'] or flop:
					print(player_action)
					self.free_throw = True
					if self.offensiveplay:
						self.free_throw_shooter = self.player
						self.FreeThrow.start(self.screen, self.player)
					elif self.deffensiveplay:
						self.free_throw_shooter = self.opp_bots[0]
						self.FreeThrow.start(self.screen, self.opp_bots[0])
					self.FreeThrow.end()
					self.free_throw = False
					self.update_play(self.player, True)

		if self.basketball:
			self.basketball.update(dt)
			
		self.show_niceshot(dt)

		if not self.ball_holder_updated:
			if ball_holder != self.ball_holder:
				self.update_play(ball_holder)

		if self.outOfBounds:
			self.ball = False
			self.snap = False
			self.qtr += 1

		if self.ball_scored_info:
			self.animation_wait_timer += dt
			if self.animation_wait_timer > 1.2:
				self.animation_wait_timer = 0
				self.finish_scored()

		if self.ball_rebound_pos:
			self.animation_wait_timer += dt
			if self.animation_wait_timer > 0.5:
				self.animation_wait_timer = 0
				self.finish_rebound()


		self.draw_sound_toggle(dt, mouse)
		pygame.display.update()


