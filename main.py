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
        self.upthescore = True
        self.outOfBounds = False
        self.outOfBounds2 = False
        self.inbounder_is_active = True
        self.snap = False
        self.menu = False
        self.team = "knicks"
        self.selected_player = "brunson"
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
        
        self.ball_holder = self.player

    # Functions
    
    def basketball_scored(self, ball_data):
        self.score[0] += ball_data.get('point_value', 1)
        self.niceshot_timer = self.niceshot_timer_dur
        
    def basketball_done(self, pos, scored):
        self.basketball = None
        
        #random.choice(self.team_bots).give_ball()
        
    def create_basketball(self, data):
        self.score[1] += 1
        data['score'] = self.basketball_scored
        data['remove'] = self.basketball_done
        self.basketball = Basketball(data)
        #data['player'].ball = False

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
                            self.create_basketball
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
                OppBots(
                    (self.team_bots_pos[i][0] + 120, self.team_bots_pos[i][1]),
                    (self.all_sprites_group, self.bots_group),
                    self.team_bots[i],
                    team,
                    bots[i],
                    self.outOfBounds,
                )
            self.opp_bots_created = True

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
                    bot.ball = True
                    self.player.ball = False
                    self.player.passselecting = False

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
        self.player.give_ball()
        self.game_loop()
        self.start_menu()


if __name__ == "__main__":
    game = Game()
    game.run()

