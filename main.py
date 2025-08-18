import pygame
import time
import random
import math
from player import Player
from inbounder import Inbounder
from player_select import PlayerSelect
from game_loop import game_loop
from all_sprites import AllSprites
from test_ball import TestBall
from basketball import Basketball
from freethrow import *


from menus import (
	start_menu,
	render_teamselect_menu,
	teamselect_menu,
	render_playerselect_menu,
	playerselect_menu,
	howto_menu,
	render_start_screen,
	render_continue_menu,
	start_screen,
	continue_menu,
)

from tipoff.tipoff import TipOff
from tipoff.tipoff_background import Background

from team_bots import TeamBots
from opp_bots import OppBots


class Game:
	def __init__(self):
		pygame.init()
		pygame.mixer.init()
		self.WINDOW_WIDTH, self.WINDOW_HEIGHT = 1215, 812
		self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
		pygame.display.set_caption("NBA 2K25")
		self.clock = pygame.time.Clock()

		# groups
		self.all_sprites_group = AllSprites()
		self.player_group = pygame.sprite.Group()
		self.bots_group = pygame.sprite.Group()
		self.inbounder_group = pygame.sprite.Group()
		self.testball_group = pygame.sprite.Group()
		self.player_select_group = pygame.sprite.Group()

		# variables
		self.love = True
		self.upthescore = True
		self.outOfBounds = False
		self.outOfBounds2 = False
		self.offensiveplay = True
		self.deffensiveplay = False
		self.inbounder_is_active = True
		self.snap = False
		self.menu = False
		self.team = "knicks"
		self.selected_player = "brunson"
		self.free_throw = False
		self.free_throw_shooter = None
		self.winner = None
		self.ball = True
		self.bot = None
		self.team_bots_created = False
		self.opp_bots_created = False
		self.niceshot_timer = 0
		self.niceshot_timer_dur = 1

		# Menu variables
		self.passto_selected_index = 0
		self.selected_index3 = None
		self.team_selected_index = 0
		self.player_selected_index = 0
		self.continue_selected_index = 0
		self.teamselect_menu_items = ["KNICKS", "LAKERS"]
		self.teamselect_instructions = [
			"CHOOSE YOUR TEAM:",
			"",
			"USE ARROW KEYS TO SELECT",
			"PRESS ENTER TO CONTINUE",
		]
		self.continue_item = ["Continue", "Quit"]

		self.player_menu_items = ""
		self.playerselectknicks_menu_items = ["brunson", "melo", "hart", "og", "kat"]
		self.playerselectlakers_menu_items = [
			"lebron",
			"kobe",
			"reeves",
			"luka",
			"hachi",
		]

		self.team_bots_pos = []
		self.opp_bots_pos = []

		self.four_one = [
			(1500, 550),
			(1331, 395),
			(1619, 709),
			(1580, 400),
			(1600, 550),
		]

		self.three_two = [
			(1500, 550),
			(1331, 395),
			(1331, 639),
			(1580, 450),
			(1600, 700),
		]

		self.five_out = [
			(1500, 550),
			(1431, 645),
			(1319, 609),
			(1319, 391),
			(1431, 455),
		]

		self.plays = {
			"4:1": self.four_one,
			"3:2": self.three_two,
			"5out": self.five_out,
		}

		# Colors
		self.WHITE = (255, 255, 255)
		self.BLACK = (40, 40, 40)
		self.HIGHLIGHT = "green"
		self.start = True

		# fonts
		self.font = pygame.font.Font("images/font.ttf", 74)

		# data
		self.qtr = 1
		self.score = [0, 0]
		self.white = pygame.Color(255, 255, 255)

		# Backgrounds
		self.knicksbackground = pygame.image.load(
			"images/courts/knicks_court_alt.png"
		).convert()
		self.lakersbackground = pygame.image.load(
			"images/courts/lakers_court_alt.png"
		).convert()

		# Classes
		self.tipoff = TipOff()

		self.player = Player((1100, 500), (self.all_sprites_group, self.player_group), self.create_basketball)
		self.inbounder = Inbounder(
			(250, 350),
			self.inbounder_group,
			self.inbounder_is_active,
			self.snap,
		)

		self.team_bots = []
		self.opp_bots = []

		self.FreeThrow = FreeThrow(self)
		
		self.basketball = None
		self.testball = TestBall(
			(200, 700),
			(
				self.testball_group,
				self.all_sprites_group,
				self.player_group,
				self.bots_group,
			),
		)
		self.testball2 = TestBall(
			(1960, 700),
			(
				self.testball_group,
				self.all_sprites_group,
				self.player_group,
				self.bots_group,
			),
		)

		# channels
		if not hasattr(self, "start_channel"):
			self.start_channel = pygame.mixer.Channel(0)

		if not hasattr(self, "tipoff_channel"):
			self.tipoff_channel = pygame.mixer.Channel(1)

		if not hasattr(self, "game_channel"):
			self.game_channel = pygame.mixer.Channel(2)

		# Instructions
		self.instructions = [
			"HOW TO PLAY:",
			"",
			"OFFENSIVE MOVES:",
			"-PASS | A KEY",
			"-SHOOT | W KEY",
			"-SPIN | S AND LEFT OR RIGHT ARROW KEYS",
			"-HALF SPIN | AS AND LEFT OR RIGHT ARROW KEYS",
			"-PUMP | SHIFT KEY",
			"-SIDE STEP | SPACEBAR AND UP OR DOWN KEY",
			"-STEP BACK | SHIFT AND LEFT OR RIGHT KEY",
			"-DUNK | D KEY",
			"-EUROSTEP | SPACEBAR AND SHIFT KEYS",
			"FLOP | WAD KEYS",
			"BALL BEHIND THE BACK | SA KEYS",
			"SWITCH HANDS | SD KEYS" "",
			"DEFENSIVE MOVES:",
			"-BLOCK | W KEY",
			"-SUMMON 2ND MAN | A KEY",
			"-STEAL | D AND LEFT OR RIGHT ARROW KEYS",
			"-DRAYMOND | S KEY",
		]

		# images/sounds
		self.music_on = False
		self.music_toggle_anim_time = -1
		self.start_music = pygame.mixer.Sound("images/sounds/start.ogg")
		self.start_music.set_volume(0.2)

		self.game_music = pygame.mixer.Sound("images/sounds/game_music.ogg")
		self.game_music.set_volume(0.2)

		self.highlight_sound = pygame.mixer.Sound("images/sounds/highlight.ogg")
		self.highlight_sound.set_volume(0.05)

		self.confirm_sound = pygame.mixer.Sound("images/sounds/confirm.ogg")
		self.confirm_sound.set_volume(0.05)

		self.start_sound = pygame.mixer.Sound("images/sounds/start_sound.ogg")
		self.start_sound.set_volume(0.05)

		self.tipoff_music = pygame.mixer.Sound("images/sounds/tipoff_music.ogg")
		self.tipoff_music.set_volume(0.2)

		self.tipoff_win_sound = pygame.mixer.Sound("images/sounds/tipoff_win.ogg")
		self.tipoff_win_sound.set_volume(0.05)

		self.tipoff_lose_sound = pygame.mixer.Sound("images/sounds/tipoff_lose.ogg")
		self.tipoff_lose_sound.set_volume(0.05)

		# Load background (Tipoff)
		self.background = None
		self.transparent_background = Background().generate_background()
		
		self.ball_holder = None
		self.ball_holder_updated = None
		self.ball_scored_info = None
		self.ball_scored_pos = None
		self.ball_rebound_pos = None
		self.animation_wait_timer = 0
		self.same_team_count = 0

	# Functions
	
	def get_closest_bot(self, pos):
		bots = [bot for bot in self.team_bots + self.opp_bots if bot is not self.player]
		closest = None
		closest_dist = float('inf')
		for bot in bots:
			dist = (pos - bot.position).magnitude()
			if dist < closest_dist:
				closest_dist = dist
				closest = bot
		return closest or self.player

	def give_ball(self, player):
		if self.free_throw:
			return

		if self.basketball:
			self.basketball.remove()
			self.basketball = None

		if self.ball_holder:
			if self.ball_holder.ball:
				self.ball_holder.take_ball()

		player.give_ball()
		self.ball_holder = player
		self.ball_holder_updated = True

	def finish_scored(self):
		print('scored')
		self.FreeThrow.basketball_event('score')
		three_pointer = abs(self.ball_scored_info.get('distance').x) > 450
		point_value = 2
		if three_pointer:
			point_value = 3
			
		if self.ball_scored_info.get('side') == "left":
			self.score[1] += point_value
		else:
			self.score[0] += point_value
		
		closest = self.get_closest_bot(self.ball_scored_pos)
		if self.offensiveplay:
			self.update_play(closest)
		elif self.deffensiveplay:
			self.update_play(self.player)

		self.ball_scored_info = None
		self.ball_scored_pos = None
		if self.basketball:
			self.basketball.remove()
			self.basketball = None
	
	def basketball_scored(self, ball_info):
		self.ball_rebound_pos = None
		self.basketball.direction = pygame.math.Vector2(0,0)
		if self.ball_scored_info:
			return
		self.niceshot_timer = self.niceshot_timer_dur
		self.ball_scored_info = ball_info
		self.ball_scored_pos = self.basketball.pos.copy()
		
		if self.free_throw:
			self.finish_scored()

	def update_play(self, player, show_offense_screen=False):
		offense = isinstance(player, (TeamBots, Player))
		if self.ball_holder and self.deffensiveplay != offense:
			self.give_ball(player)
			return
		self.offensiveplay = offense
		self.deffensiveplay = not offense

		if self.offensiveplay:
			if show_offense_screen:
				self.player.offensiveplay_screen(self.screen)
			for bot in self.team_bots: 
				if bot != self.player:
					bot.offensive_position()
			for pos in self.opp_bots:
				pos.offensive_position()
 
		
		if self.deffensiveplay:
			self.player.deffensiveplay_screen(self.screen)
			for bot in self.team_bots:
				if bot != self.player: 
					bot.deffensive_position()
			for bot in self.opp_bots:
					bot.deffensive_position()
			self.player.position = pygame.math.Vector2(300,500)

		self.give_ball(player)

	def finish_rebound(self):
		self.FreeThrow.basketball_event('rebound')

		if self.same_team_count > 3:
			closest = random.choice(self.opp_bots)
			self.same_team_count = 0
		else:
			closest = self.get_closest_bot(self.ball_rebound_pos)
		if self.offensiveplay:
			self.same_team_count += 1
			self.update_play(closest)
		elif self.deffensiveplay:
			self.update_play(self.player, True)

		self.ball_rebound_pos = None
		if self.basketball:
			self.basketball.remove()
			self.basketball = None

	def basketball_rebound(self, pos):
		self.ball_scored_info = None
		self.ball_scored_pos = None
		if self.ball_rebound_pos:
			return
		self.ball_rebound_pos = self.basketball.pos.copy()

		if self.free_throw:
			self.finish_rebound()
		
	def basketball_catch(self, pos, player):
		self.update_play(player)
		if self.basketball:
			self.basketball.remove()
			self.basketball = None
		
	def create_basketball(self, data):
		if self.basketball:
			self.basketball.remove()
			self.basketball = None
		data['score'] = self.basketball_scored
		data['rebound'] = self.basketball_rebound
		data['catch'] = self.basketball_catch
		data['group'] = self.all_sprites_group
		self.basketball = Basketball(data)

	def draw_sound_toggle(self, dt, mouse):
		toggle_x = 90
		toggle_y = self.WINDOW_HEIGHT - 40
		button_width = 50
		button_height = 30
		font_size = 35
		off_color_bg = 'grey'
		on_color_bg = 'green'
		off_color_switch = 'white'
		on_color_switch = 'white'
		switch_anim_time = 80 # milliseconds

		if mouse:
			if mouse[0] > toggle_x and mouse[0] < toggle_x + button_width:
				if mouse[1] > toggle_y and mouse[1] < toggle_y + button_height:
					self.music_on = not self.music_on
					if self.music_on:
						self.music_toggle_anim_time = 0
					else:
						self.music_toggle_anim_time = 1

		# SCORE text
		my_font = pygame.font.Font("images/font.ttf", font_size)
		font_surface = my_font.render("MUSIC", True, "white")
		font_rect = font_surface.get_rect()
		font_rect.midtop = (toggle_x - font_size - 5, toggle_y)
		self.screen.blit(font_surface, font_rect)
		
		# toggle button
		anim_mult = 1/(switch_anim_time/1000)
		if self.music_on:
			if self.music_toggle_anim_time < 1:
				self.music_toggle_anim_time += anim_mult * dt
			else:
				self.music_toggle_anim_time = 1
			pygame.draw.rect(self.screen, on_color_bg,(toggle_x, toggle_y, button_width, button_height))
			anim_pos_x = toggle_x + self.music_toggle_anim_time * (button_width - button_height)
			pygame.draw.rect(self.screen, on_color_switch, (anim_pos_x+4, toggle_y+4, button_height-8, button_height-8))
			self.game_music.set_volume(0.2)
		else:
			if self.music_toggle_anim_time > 0:
				self.music_toggle_anim_time -= anim_mult * dt
			else:
				self.music_toggle_anim_time = 0
			pygame.draw.rect(self.screen, off_color_bg, (toggle_x, toggle_y, button_width, button_height))
			anim_pos_x = toggle_x + (self.music_toggle_anim_time * (button_width - button_height))
			pygame.draw.rect(self.screen, on_color_switch, (anim_pos_x+4, toggle_y+4, button_height-8, button_height-8))
			self.game_music.set_volume(0.0)

	def show_niceshot(self, dt):
		if self.niceshot_timer <= 0:
			return
		self.niceshot_timer -= dt
		frac = self.niceshot_timer / self.niceshot_timer_dur
		easing = math.cos((frac**10 - 0.23)*math.pi) * 0.5 + 0.5
		my_font = pygame.font.Font("images/font.ttf", int(100 * easing))
		speed_surface = my_font.render("NICE SHOT", True, "green")
		speed_rect = speed_surface.get_rect()
		speed_rect.midtop = (750, 100)
		self.screen.blit(speed_surface, speed_rect)

	def player_select(self):
		dt = self.clock.tick() / 1000

		selected_player = self.player_menu_items[self.player_selected_index]
		self.player_select_group.update(selected_player, dt)
		self.player_select_group.draw(self.screen)

	def switch_team(self, new_team):
		self.team = new_team.lower()

		if self.team == "knicks":
			self.select_team = {
				"knicks": [
					("brunson", (215, 400)),
					("melo", (415, 400)),
					("hart", (615, 400)),
					("og", (815, 400)),
					("kat", (1015, 400)),
				]
			}
		else:
			self.select_team = {
				"lakers": [
					("lebron", (215, 400)),
					("kobe", (415, 400)),
					("reeves", (615, 400)),
					("luka", (815, 400)),
					("hachi", (1015, 400)),
				]
			}

		self.player_select_group.empty()

		for team_name, players in self.select_team.items():
			for name, pos in players:
				setattr(
					self,
					f"{team_name}_{name}_select",
					PlayerSelect(pos, self.player_select_group, team_name, name),
				)

	def spawn_team_bots(self):
		if not self.team_bots_created:
			if self.team == "knicks":
				bots = self.playerselectknicks_menu_items
				team = "knicks"
			elif self.team == "lakers":
				bots = self.playerselectlakers_menu_items
				team = "lakers"

			random.shuffle(bots)

			play_name, play_coords = random.choice(list(self.plays.items()))

			for i in range(5):
				coords = play_coords[i]

				pos_x = coords[0]
				pos_y = coords[1]

				target_pos = [self.four_one[i], self.three_two[i], self.five_out[i]]

				if self.playerselectknicks_menu_items[i] == self.selected_player:
					self.team_bots.append(self.player)

					self.team_bots_pos.append(
						(self.player.position[0], self.player.position[1])
					)
				else:
					self.team_bots_pos.append((pos_x, pos_y))

					self.team_bots.append(
						TeamBots(
							(pos_x, pos_y),
							(self.all_sprites_group, self.bots_group),
							self.player,
							team,
							bots[i],
							play_name,
							self.outOfBounds,
							target_pos,
							self.create_basketball,
						)
					)
			self.team_bots_created = True
			self.player.team_bots = self.team_bots
			 

	def spawn_opp_bots(self):
		if not self.opp_bots_created:
			if self.team == "knicks":
				bots = self.playerselectlakers_menu_items
				team = "knicks"
			elif self.team == "lakers":
				bots = self.playerselectknicks_menu_items
				team = "lakers"

			random.shuffle(bots)

			for i in range(5):
				
				self.opp_bots.append(OppBots(
					(self.team_bots_pos[i][0] + 120, self.team_bots_pos[i][1]),
					(self.all_sprites_group, self.bots_group),
					self.team_bots[i],
					team,
					bots[i],
					self.outOfBounds,
					self.create_basketball,
				))

			self.opp_bots_created = True
			self.player.opp_bots = self.opp_bots

	def show_qtr(self, qtr, screen):
		self.qtr = qtr % 4
		my_font = pygame.font.Font("images/font.ttf", 50)
		if self.qtr == 1:
			down_surface = my_font.render("1ST QTR", True, "white")
		elif self.qtr == 2:
			down_surface = my_font.render("2ND QTR", True, "white")
		elif self.qtr == 3:
			down_surface = my_font.render("3RD QTR", True, "white")
		elif self.qtr == 0:
			down_surface = my_font.render("4TH QTR", True, "white")

		down_rect = down_surface.get_rect()
		down_rect.midtop = (615, 5)
		screen.blit(down_surface, down_rect)

		return self.qtr

	def show_score(self):
		my_font = pygame.font.Font("images/font.ttf", 50)
		score_surface = my_font.render(
			f"SCORE: {self.score[0]} vs {self.score[1]}", True, self.white
		)
		score_rect = score_surface.get_rect()
		score_rect.midtop = (1050, 5)
		self.screen.blit(score_surface, score_rect)

	def show_text(self, text, x=0, y=0, color=(255,255,255)):
		my_font = pygame.font.Font("images/font.ttf", 120)
		text_surface = my_font.render(text, True, color)
		text_rect = text_surface.get_rect()
		text_rect.midtop = (x, y)
		self.screen.blit(text_surface, text_rect)
		pygame.display.flip()
		time.sleep(1)


	def show_passselectionscreenlogic(self, events):
		inc = 1
		for event in events:   
			if event.type == pygame.KEYDOWN:
				
				self.highlight_sound.play()
				if event.key == pygame.K_LEFT:
					self.highlight_sound.play()
					self.passto_selected_index = (self.passto_selected_index - inc) % len(
						self.team_bots
					)
					inc = -1

				elif event.key == pygame.K_RIGHT:
					self.highlight_sound.play()
					self.passto_selected_index = (self.passto_selected_index + inc) % len(
						self.team_bots 
					)
				elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE: 
					bot = self.team_bots[self.passto_selected_index]
					self.player.bot = bot
					self.update_play(bot)
					self.player.passselecting = False
					self.passto_selected_index = 0

		bot = self.team_bots[self.passto_selected_index]
		if bot == self.player:
			self.passto_selected_index += inc
			bot = self.team_bots[self.passto_selected_index]
		pos_x = bot.position[0] - self.all_sprites_group.offset.x
		pos_y = bot.position[1] - 120
		pygame.draw.circle(self.screen, "Green", (pos_x, pos_y), 15)

	
	def show_passselectionscreen(self, events):
	
		my_font = pygame.font.Font("images/font.ttf", 65)
		speed_surface = my_font.render("SELECT A PLAYER TO PASS TO", True, "yellow")
		speed_rect = speed_surface.get_rect()
		speed_rect.midtop = (620, 100)
		self.screen.blit(speed_surface, speed_rect)    
		self.show_passselectionscreenlogic(events)

	def show_startscreen(self):

		my_font = pygame.font.Font("images/font.ttf", 45)
		speed_surface = my_font.render("NBA 2K25", True, "yellow")
		speed_rect = speed_surface.get_rect()
		speed_rect.midtop = (320, 480)
		self.screen.blit(speed_surface, speed_rect)

	def show_startscreensub(self):

		my_font = pygame.font.Font("images/font.ttf", 30)
		speed_surface = my_font.render("A DN INDUSTRIES PRODUCT", True, "yellow")
		speed_rect = speed_surface.get_rect()
		speed_rect.midtop = (320, 515)
		self.screen.blit(speed_surface, speed_rect)

	def show_startscreensub1(self):
		if int(time.time() * 2) % 2 == 0:
			my_font = pygame.font.Font("images/font.ttf", 55)
			speed_surface = my_font.render("PRESS S TO START THE GAME", True, "white")
			speed_rect = speed_surface.get_rect()
			speed_rect.midtop = (806, 605)
			self.screen.blit(speed_surface, speed_rect)

	def logo(self):
		implogo = pygame.image.load("images/logo.png").convert_alpha()
		self.screen.blit(
			implogo,
			pygame.Rect(105, 100, 10, 10),
		)

	def logolakers(self):
		implogolakers = pygame.image.load("images/logolakers.png").convert_alpha()
		self.screen.blit(
			implogolakers,
			pygame.Rect(700, 225, 40, 10),
		)

	def logolakers1(self):
		implogolakers = pygame.image.load("images/logolakers.png").convert_alpha()
		self.screen.blit(
			implogolakers,
			pygame.Rect(150, 175, 10, 10),
		)

	def logoknx(self):
		implogoknx = pygame.image.load("images/logoknx.png").convert_alpha()
		self.screen.blit(
			implogoknx,
			pygame.Rect(210, 225, 10, 10),
		)

	def logoknx1(self):
		implogoknx = pygame.image.load("images/logoknx.png").convert_alpha()
		self.screen.blit(
			implogoknx,
			pygame.Rect(170, 125, 10, 10),
		)

	def howto(self, lines, color, start_pos, line_spacing=5):
		font = pygame.font.Font("images/font.ttf", 30)
		x, y = start_pos
		for line in lines:
			text_surface = font.render(line, True, color)
			self.screen.blit(text_surface, (x, y))
			y += font.get_height() + line_spacing

	def game_loop(self):
		game_loop(self)

	def start_menu(self):
		start_menu(self)

	def playerselect_menu(self):
		playerselect_menu(self)

	def render_playerselect_menu(self):
		render_playerselect_menu(self)

	def teamselect_menu(self):
		teamselect_menu(self)

	def render_teamselect_menu(self):
		render_teamselect_menu(self)

	def howto_menu(self):
		howto_menu(self)

	"""Tipoff"""

	def win_condition(self):
		my_font = pygame.font.Font("images/font.ttf", 50)
		score_surface = my_font.render("First to 5 Wins", True, "white")
		score_rect = score_surface.get_rect()
		score_rect.midtop = (1030, 5)
		self.screen.blit(score_surface, score_rect)

	def gameplay_instructions(self):
		my_font = pygame.font.Font("images/font.ttf", 50)
		score_surface = my_font.render("Jump: Spacebar", True, "white")
		score_rect = score_surface.get_rect()
		score_rect.midtop = (190, 5)
		self.screen.blit(score_surface, score_rect)

	def render_start_screen(self):
		render_start_screen(self)

	def start_screen(self):
		start_screen(self)

	def render_continue_menu(self):
		render_continue_menu(self)

	def continue_menu(self):
		continue_menu(self)

	def run(self):
		self.update_play(self.player)
		self.game_loop()
		self.start_menu()


if __name__ == "__main__":
	game = Game()
	game.run()


