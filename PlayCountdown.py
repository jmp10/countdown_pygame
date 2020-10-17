import pygame
from random import randint, sample, choice, shuffle
from math import floor


class Tile:
    def __init__(self, char):
        self.char = char
        self.link = "Countdown Tiles/Countdown" + str(self.char) + ".png"
        self.image = pygame.image.load(self.link).convert()


class Light:
    def __init__(self, number):
        self.link = "Countdown Clock Lights/ClockLight" + str(number) + ".png"
        self.image = pygame.image.load(self.link).convert_alpha()
        self.image_rect = self.image.get_rect(center=clock_center)


pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)  # set the window size (fullscreen)
# screen = pygame.display.set_mode((1920, 1080))  # set the window size (not fullscreen)
clock = pygame.time.Clock()  # for frame rate

done = False
totally_done = False
intro = True


# colors
white = (255, 255, 255)
medium_blue = (55, 119, 222)
tile_blue = (8, 72, 147)  # color of the letter and number tiles
board_blue = (54, 83, 167)  # color of the surrounding board
green = (127, 255, 42)  # for target number
red = (255, 42, 42)  # for buzzer's exclamation points

inactive_color = tile_blue
active_color = medium_blue

# fonts
futura = pygame.font.Font("Fonts to Use/Futura Bold.otf", 55)
futura_names = pygame.font.Font("Fonts to Use/Futura Bold.otf", 20)
futura_scores = pygame.font.Font("Fonts to Use/Futura Bold.otf", 65)
futura_final_scores = pygame.font.Font("Fonts to Use/Futura Bold.otf", 75)
futura_cond = pygame.font.Font("Fonts to Use/Futura Condensed Bold.otf", 45)
digital = pygame.font.Font("Fonts to Use/DSEG7Classic-BoldItalic.ttf", 100)
rodin = pygame.font.Font("Fonts to Use/FOT-NewRodinProN-EB.otf", 130)

# images
background_l = pygame.image.load("Countdown Assets/Countdown Studio - Bottom.png").convert()
background_n = pygame.image.load("Countdown Assets/Countdown Studio - Bottom Numbers.png").convert()
background_empty = pygame.image.load("Countdown Assets/Countdown Empty Background.png").convert()
clock_lines = pygame.image.load("Countdown Assets/Countdown Clock Lines.png").convert_alpha()

clock_hand = pygame.image.load("Countdown Assets/Countdown Clock Hand.png").convert_alpha()
clock_hand = pygame.transform.scale(clock_hand, (33, 608))

clock_center = (959.5, 341)
clock_hand_rect = clock_hand.get_rect(center=clock_center)
clock_on = False
music_on = False
paused = True
angle = 0
light_num = 0

# sounds
conundrum_buzzer = pygame.mixer.Sound("Music/Countdown Buzzer.wav")
conundrum_bell = pygame.mixer.Sound("Music/Countdown Bell.wav")

# for names
p1_name_rect_center = (592.4, 813)
p2_name_rect_center = (1326.4, 813)
p1_name = "PLAYER 1"
p2_name = "PLAYER 2"
player1 = futura_names.render(p1_name, True, white)
player2 = futura_names.render(p2_name, True, white)
player1_rect = player1.get_rect(center=p1_name_rect_center)
player2_rect = player2.get_rect(center=p2_name_rect_center)

# for scores
p1_score_rect_top, p1_score_rect_right = 706, 915
p2_score_rect_top, p2_score_rect_right = 706, 1136
p1_score = 0
p2_score = 0

# for creating tiles
sprite_list = []
all_tiles = {}
for char in list("ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789") + ["10", "25", "50", "75", "100", "12", "37", "62", "87"]:
    all_tiles[char] = Tile(char)

# for creating clock lights
all_lights = {}
for num in range(31):
    all_lights[num] = Light(num)

# initial consonant and vowel piles
consonant_pile = list(
    "B" * 2 + "C" * 3 + "D" * 6 + "F" * 2 + "G" * 4 + "H" * 2 + "J" * 1 + "K" * 1 + "L" * 5 + "M" * 4 + "N" * 7 +
    "P" * 4 + "Q" * 1 + "R" * 9 + "S" * 9 + "T" * 9 + "V" * 2 + "W" * 2 + "X" * 1 + "Y" * 1 + "Z" * 1)
vowel_pile = list("A" * 15 + "E" * 21 + "I" * 13 + "O" * 13 + "U" * 5)
picked_letters = []
picked_letters_text = []

# initial number piles
large_pile = ["25", "50", "75", "100"]
large_pile_tricky = ["12", "37", "62", "87"]
small_pile = [str(i) for i in range(1, 11)]*2
picked_numbers = []
picked_numbers_text = []
numbers_to_show = 0

# for target number
target_showing = False
target = 100
target_rect_center = (518, 968)
target_text = digital.render(str(target), True, green)
target_rect = target_text.get_rect(center=target_rect_center)
target_counter = 0

# for conundrum buzzing and showing
p1_buzzed = False
p2_buzzed = False
exclamation = rodin.render("!", True, red)
p1_exclamation_rect = exclamation.get_rect(center=(495, 690))
p2_exclamation_rect = exclamation.get_rect(center=(1425, 690))
hidden = True
conundrum_overlay = pygame.image.load("Countdown Assets/Countdown Conundrum Overlay.png").convert()
with open("Conundrums.txt") as file:
    conundrum_list = [line.rstrip('\n') for line in file]


# for final score screen
p1_name_rect_final = pygame.Rect(495, 431, 660, 110)
p1_name_text_final = futura.render(p1_name, True, white)
p2_name_rect_final = pygame.Rect(495, 571, 660, 110)
p2_name_text_final = futura.render(p2_name, True, white)

p1_score_rect_final = pygame.Rect(1230, 431, 195, 110)
p2_score_rect_final = pygame.Rect(1230, 571, 195, 110)


def text_objects(text, font, color):
    text_surface = font.render(text, True, color)
    return text_surface, text_surface.get_rect()


def draw_button(button):
    # draw the button rect and the text surface
    pygame.draw.rect(screen, button['color'], button['rect'])
    screen.blit(button['text'], button['text rect'])


def create_button(msg, x, y, w, h, callback):
    # The button is a dictionary consisting of the rect, text, text rect, color and the callback function.
    text_surf = futura_cond.render(msg, True, white)
    button_rect = pygame.Rect(x, y, w, h)
    text_rect = text_surf.get_rect(center=button_rect.center)
    button = {
        'msg': msg,
        'rect': button_rect,
        'text': text_surf,
        'text rect': text_rect,
        'color': inactive_color,
        'callback': callback,
        }
    return button


def rot_center(image, rect, angle):
    # rotate an image while keeping its center
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = rot_image.get_rect(center=rect.center)
    return rot_image, rot_rect


def pick_consonant():  # pick a consonant from the pile, and append its Tile to the tile stack
    picked_letter = consonant_pile.pop(randint(0, len(consonant_pile) - 1))
    picked_letters_text.append(picked_letter)
    picked_letters.append(all_tiles[picked_letter])


def pick_vowel():  # pick a vowel from the pile, and append its Tile to the tile stack
    picked_letter = vowel_pile.pop(randint(0, len(vowel_pile) - 1))
    picked_letters_text.append(picked_letter)
    picked_letters.append(all_tiles[picked_letter])


def pick_numbers(num_large):  # pick some large and some small numbers and append their Tiles to the tile stack
    global picked_numbers_text, picked_numbers
    num_large = int(num_large)
    large_numbers = sample(large_pile, k=num_large)
    small_numbers = sample(small_pile, k=6-num_large)
    picked_numbers_text += large_numbers
    picked_numbers_text += small_numbers
    picked_numbers += [all_tiles[k] for k in picked_numbers_text]


def pick_target():  # pick a 3-digit target number and render it
    global target_showing, target, target_text, target_rect
    target_showing = True
    target = randint(100, 999)
    target_text = digital.render(str(target), True, green)
    target_rect = target_text.get_rect(center=target_rect_center)


def show_num_increment():  # for displaying numbers in the numbers round one after the other
    global numbers_to_show
    numbers_to_show += 1


def scramble(puzzle):  # for generating the scrambled conundrum
    puzzle1 = list(puzzle)
    shuffle(puzzle1)
    return "".join(puzzle1)


def start_clock():
    global clock_on, paused
    clock_on = True
    paused = not paused


def start_clock_conundrum():
    global clock_on, hidden
    clock_on = True
    hidden = False


def increase_p1_score():
    global p1_score
    p1_score += 1


def decrease_p1_score():
    global p1_score
    p1_score -= 1


def increase_p2_score():
    global p2_score
    p2_score += 1


def decrease_p2_score():
    global p2_score
    p2_score -= 1


def reset_round():  # reset everything
    global clock_on, music_on, angle, light_num, picked_letters, picked_letters_text, picked_numbers, \
        picked_numbers_text, large_pile, small_pile, numbers_to_show, target_counter, target_showing,\
        p1_buzzed, p2_buzzed, hidden, paused, done
    clock_on, music_on = False, False
    pygame.mixer.music.load("Music/CountdownClock.mp3")
    angle = 0
    light_num = 0

    picked_letters, picked_letters_text = [], []
    picked_numbers, picked_numbers_text = [], []
    numbers_to_show = 0
    target_counter = 0
    target_showing = False

    p1_buzzed, p2_buzzed = False, False
    hidden = True
    paused = True
    done = True


def reset_letters():  # reset the letters stack at the end of the game
    global consonant_pile, vowel_pile
    consonant_pile = list(
        "B" * 2 + "C" * 3 + "D" * 6 + "F" * 2 + "G" * 4 + "H" * 2 + "J" * 1 + "K" * 1 + "L" * 5 + "M" * 4 + "N" * 7 +
        "P" * 4 + "Q" * 1 + "R" * 9 + "S" * 9 + "T" * 9 + "V" * 2 + "W" * 2 + "X" * 1 + "Y" * 1 + "Z" * 1)
    vowel_pile = list("A" * 15 + "E" * 21 + "I" * 13 + "O" * 13 + "U" * 5)


def quit_game():
    global totally_done
    totally_done = True


def letters_game():
    vowel_button = create_button("VOWEL", 55, 885, 250, 75, pick_vowel)
    consonant_button = create_button("CONSONANT", 55, 975, 250, 75, pick_consonant)
    start_clock_button = create_button("", 740, 120, 440, 440, start_clock)
    continue_button = create_button("CONTINUE", 1615, 930, 250, 75, reset_round)
    p1_increase_button = create_button("", 767, 676, 166, 60, increase_p1_score)
    p1_decrease_button = create_button("", 767, 736, 166, 60, decrease_p1_score)
    p2_increase_button = create_button("", 987, 676, 166, 60, increase_p2_score)
    p2_decrease_button = create_button("", 987, 736, 166, 60, decrease_p2_score)
    button_list = [vowel_button, consonant_button, start_clock_button, continue_button,
                   p1_increase_button, p1_decrease_button, p2_increase_button, p2_decrease_button]

    pygame.mixer.music.stop()
    pygame.mixer.music.load("Music/CountdownClock.mp3")

    global done, totally_done
    done = False
    while not done and not totally_done:
        keys = pygame.key.get_pressed()
        screen.blit(background_l, (0, 0))
        clock_hand_copy = clock_hand.copy()

        for event in pygame.event.get():
            if event.type == pygame.QUIT or keys[pygame.K_ESCAPE]:
                totally_done = True  # if you quit the program, end the loop

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for button in button_list:
                    if button["rect"].collidepoint(event.pos[0], event.pos[1]):
                        button["callback"]()

            elif event.type == pygame.MOUSEMOTION:
                # When the mouse gets moved, change the color of the buttons if they collide with the mouse.
                for button in button_list:
                    if button['rect'].collidepoint(event.pos[0], event.pos[1]):
                        button['color'] = active_color
                    else:
                        button['color'] = inactive_color

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:  # pick a consonant
                    pick_consonant()
                if event.key == pygame.K_v:  # pick a vowel
                    pick_vowel()
                if event.key == pygame.K_SPACE:  # start, pause, or unpause the clock
                    start_clock()
                    if paused:
                        pygame.mixer.music.pause()
                    else:
                        pygame.mixer.music.unpause()
                if event.key == pygame.K_RIGHT:  # continue (i.e. reset the round)
                    reset_round()

        # blit names
        screen.blit(player1, player1_rect)
        screen.blit(player2, player2_rect)

        # blit scores
        p1_score_render = futura_scores.render(str(p1_score), True, white)
        p2_score_render = futura_scores.render(str(p2_score), True, white)
        p1_score_rect = p1_score_render.get_rect(top=p1_score_rect_top, right=p1_score_rect_right)
        p2_score_rect = p2_score_render.get_rect(top=p2_score_rect_top, right=p2_score_rect_right)
        screen.blit(p1_score_render, p1_score_rect)
        screen.blit(p2_score_render, p2_score_rect)

        # showing the letter buttons and tiles
        if len(picked_letters) < 9:
            draw_button(vowel_button)
            draw_button(consonant_button)

        for idx, letter in enumerate(picked_letters):
            screen.blit(pygame.transform.scale(letter.image, (120, 120)),
                        (360+135*idx, 907.5))

        # print(picked_letters_text)

        # countdown clock
        if not clock_on:  # if it's not on, just blit the clock lines and hand
            screen.blit(clock_lines, clock_lines.get_rect(center=clock_center))
            screen.blit(clock_hand, (943.5, 35.1))
        else:
            # play the music
            global music_on
            if not music_on:
                pygame.mixer.music.play(0)
                music_on = True

            # update the angle
            global angle
            global light_num
            if angle > -179.8 and not paused:
                angle -= .2
                light_num += .2/6

            # blit the lights
            j = floor(light_num)
            screen.blit(all_lights[j].image, all_lights[j].image_rect)

            # blit the lines
            screen.blit(clock_lines, clock_lines.get_rect(center=clock_center))

            # blit the hand
            clock_hand_copy, new_rect = rot_center(clock_hand_copy, clock_hand_rect, angle)
            screen.blit(clock_hand_copy, new_rect)
            if angle <= -179.8:
                draw_button(continue_button)

        fps = futura.render(str(int(clock.get_fps())), True, white)  # for displaying frame rate
        screen.blit(fps, (50, 50))

        pygame.display.update()
        clock.tick(30)  # for frame rate


def numbers_game():
    zero_large_button = create_button("0", 55, 885, 75, 75, pick_numbers)
    one_large_button = create_button("1", 142.5, 885, 75, 75, pick_numbers)
    two_large_button = create_button("2", 230, 885, 75, 75, pick_numbers)
    three_large_button = create_button("3", 99, 975, 75, 75, pick_numbers)
    four_large_button = create_button("4", 186, 975, 75, 75, pick_numbers)
    show_num_button = create_button("", 693, 907, 867, 120, show_num_increment)
    target_button = create_button("", 360, 907, 318, 120, pick_target)

    start_clock_button = create_button("", 740, 120, 440, 440, start_clock)
    continue_button = create_button("CONTINUE", 1615, 930, 250, 75, reset_round)
    p1_increase_button = create_button("", 767, 676, 166, 60, increase_p1_score)
    p1_decrease_button = create_button("", 767, 736, 166, 60, decrease_p1_score)
    p2_increase_button = create_button("", 987, 676, 166, 60, increase_p2_score)
    p2_decrease_button = create_button("", 987, 736, 166, 60, decrease_p2_score)
    button_list = [zero_large_button, one_large_button, two_large_button, three_large_button, four_large_button,
                   show_num_button, target_button, start_clock_button, continue_button, p1_increase_button,
                   p1_decrease_button, p2_increase_button, p2_decrease_button]
    num_large_buttons = [zero_large_button, one_large_button, two_large_button, three_large_button, four_large_button]

    pygame.mixer.music.stop()
    pygame.mixer.music.load("Music/CountdownClock.mp3")

    global done, totally_done
    done = False
    while not done and not totally_done:
        keys = pygame.key.get_pressed()
        screen.blit(background_n, (0, 0))
        clock_hand_copy = clock_hand.copy()

        for event in pygame.event.get():
            if event.type == pygame.QUIT or keys[pygame.K_ESCAPE]:
                totally_done = True  # if you quit the program, end the whole thing

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for button in button_list:
                    if button["rect"].collidepoint(event.pos[0], event.pos[1]) and button in num_large_buttons:
                        button["callback"](button["msg"])
                    elif button["rect"].collidepoint(event.pos[0], event.pos[1]):
                        button["callback"]()

            elif event.type == pygame.MOUSEMOTION:
                # When the mouse gets moved, change the color of the buttons if they collide with the mouse.
                for button in button_list:
                    if button['rect'].collidepoint(event.pos[0], event.pos[1]):
                        button['color'] = active_color
                    else:
                        button['color'] = inactive_color

            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:  # pick num large
                    pick_numbers(pygame.key.name(event.key))
                if event.key == pygame.K_SPACE:  # start, pause, or unpause the clock
                    start_clock()
                    if paused:
                        pygame.mixer.music.pause()
                    else:
                        pygame.mixer.music.unpause()
                if event.key == pygame.K_RIGHT:  # continue (i.e. reset the round)
                    reset_round()

        # blit names
        screen.blit(player1, player1_rect)
        screen.blit(player2, player2_rect)

        # blit scores
        p1_score_render = futura_scores.render(str(p1_score), True, white)
        p2_score_render = futura_scores.render(str(p2_score), True, white)
        p1_score_rect = p1_score_render.get_rect(top=p1_score_rect_top, right=p1_score_rect_right)
        p2_score_rect = p2_score_render.get_rect(top=p2_score_rect_top, right=p2_score_rect_right)
        screen.blit(p1_score_render, p1_score_rect)
        screen.blit(p2_score_render, p2_score_rect)

        # showing buttons, number tiles, and random target
        if len(picked_numbers) < 6:
            for i in num_large_buttons:
                draw_button(i)

        for idx, number in enumerate(picked_numbers):
            if 6-idx <= numbers_to_show:
                screen.blit(pygame.transform.scale(number.image, (132, 120)),
                            (-147*(5-idx)+1428, 907.5))

        if target_showing:
            global target_counter
            if target_counter <= 40:
                target_counter += 1
            if target_counter % 2 == 0:
                pick_target()
            screen.blit(target_text, target_rect)

        # countdown clock
        if not clock_on:  # if it's not on, just blit the clock lines and hand
            screen.blit(clock_lines, clock_lines.get_rect(center=clock_center))
            screen.blit(clock_hand, (943.5, 35.1))
        else:
            # play the music
            global music_on
            if not music_on:
                pygame.mixer.music.play(0)
                music_on = True

            # update the angle
            global angle
            global light_num
            if angle > -179.8 and not paused:
                angle -= .2
                light_num += .2/6

            # blit the lights
            j = floor(light_num)
            screen.blit(all_lights[j].image, all_lights[j].image_rect)

            # blit the lines
            screen.blit(clock_lines, clock_lines.get_rect(center=clock_center))

            # blit the hand
            clock_hand_copy, new_rect = rot_center(clock_hand_copy, clock_hand_rect, angle)
            screen.blit(clock_hand_copy, new_rect)
            if angle <= -179.8:
                draw_button(continue_button)

        fps = futura.render(str(int(clock.get_fps())), True, white)  # for displaying frame rate
        screen.blit(fps, (50, 50))

        pygame.display.update()
        clock.tick(30)  # for frame rate


def conundrum():
    start_clock_button = create_button("", 740, 120, 440, 440, start_clock_conundrum)
    continue_button = create_button("CONTINUE", 1615, 930, 250, 75, reset_round)
    p1_increase_button = create_button("", 767, 676, 166, 60, increase_p1_score)
    p1_decrease_button = create_button("", 767, 736, 166, 60, decrease_p1_score)
    p2_increase_button = create_button("", 987, 676, 166, 60, increase_p2_score)
    p2_decrease_button = create_button("", 987, 736, 166, 60, decrease_p2_score)
    button_list = [start_clock_button, continue_button, p1_increase_button, p1_decrease_button, p2_increase_button,
                   p2_decrease_button]

    conundrum_answer_text = choice(conundrum_list)
    conundrum_answer = [Tile(letter) for letter in conundrum_answer_text]
    conundrum_scramble_text = scramble(conundrum_answer_text)
    conundrum_scramble = [Tile(letter) for letter in conundrum_scramble_text]
    incorrect = [Tile(letter) for letter in "INCORRECT"]
    currently_showing = conundrum_scramble

    pygame.mixer.music.stop()
    pygame.mixer.music.load("Music/CountdownClock.mp3")

    global done, totally_done, p1_buzzed, p2_buzzed, clock_on
    done = False
    while not done and not totally_done:
        keys = pygame.key.get_pressed()
        screen.blit(background_l, (0, 0))
        clock_hand_copy = clock_hand.copy()

        for event in pygame.event.get():
            if event.type == pygame.QUIT or keys[pygame.K_ESCAPE]:
                totally_done = True  # if you quit the program, end the whole thing

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for button in button_list:
                    if button["rect"].collidepoint(event.pos[0], event.pos[1]):
                        button["callback"]()

            elif event.type == pygame.MOUSEMOTION:
                # When the mouse gets moved, change the color of the buttons if they collide with the mouse.
                for button in button_list:
                    if button['rect'].collidepoint(event.pos[0], event.pos[1]):
                        button['color'] = active_color
                    else:
                        button['color'] = inactive_color

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:  # start the clock and show the conundrum
                    start_clock_conundrum()
                if event.key == pygame.K_a and not p2_buzzed:  # p1 buzzes in (unless locked out by p2)
                    p1_buzzed = True
                    pygame.mixer.music.pause()
                    pygame.mixer.Sound.play(conundrum_bell)
                if event.key == pygame.K_l and not p1_buzzed:  # p2 buzzes in (unless locked out by p1)
                    p2_buzzed = True
                    pygame.mixer.music.pause()
                    pygame.mixer.Sound.play(conundrum_buzzer)
                if event.key == pygame.K_r:  # reset buzzes
                    p1_buzzed, p2_buzzed = False, False
                    pygame.mixer.music.unpause()
                    currently_showing = conundrum_scramble
                if event.key == pygame.K_UP:  # show the answer
                    currently_showing = conundrum_answer
                if event.key == pygame.K_DOWN:  # show incorrect
                    currently_showing = incorrect
                if event.key == pygame.K_RIGHT:  # continue (i.e. reset the round)
                    reset_round()

        # blit names
        screen.blit(player1, player1_rect)
        screen.blit(player2, player2_rect)

        # blit scores
        p1_score_render = futura_scores.render(str(p1_score), True, white)
        p2_score_render = futura_scores.render(str(p2_score), True, white)
        p1_score_rect = p1_score_render.get_rect(top=p1_score_rect_top, right=p1_score_rect_right)
        p2_score_rect = p2_score_render.get_rect(top=p2_score_rect_top, right=p2_score_rect_right)
        screen.blit(p1_score_render, p1_score_rect)
        screen.blit(p2_score_render, p2_score_rect)

        for idx, letter in enumerate(currently_showing):
            screen.blit(pygame.transform.scale(letter.image, (120, 120)),
                        (360+135*idx, 907.5))

        if hidden:
            screen.blit(conundrum_overlay, (360, 906.5))

        if p1_buzzed:
            screen.blit(exclamation, p1_exclamation_rect)
        if p2_buzzed:
            screen.blit(exclamation, p2_exclamation_rect)

        # countdown clock
        if not clock_on:  # if it's not on, just blit the clock lines and hand
            screen.blit(clock_lines, clock_lines.get_rect(center=clock_center))
            screen.blit(clock_hand, (943.5, 35.1))
        else:
            # play the music
            global music_on
            if not music_on:
                pygame.mixer.music.play(0)
                music_on = True

            # update the angle (if no one has buzzed)
            global angle
            global light_num
            if angle > -179.8 and not p1_buzzed and not p2_buzzed:
                angle -= .2
                light_num += .2 / 6

            # blit the lights
            j = floor(light_num)
            screen.blit(all_lights[j].image, all_lights[j].image_rect)

            # blit the lines
            screen.blit(clock_lines, clock_lines.get_rect(center=clock_center))

            # blit the hand
            clock_hand_copy, new_rect = rot_center(clock_hand_copy, clock_hand_rect, angle)
            screen.blit(clock_hand_copy, new_rect)
            if angle <= -179.8:
                draw_button(continue_button)

        fps = futura.render(str(int(clock.get_fps())), True, white)  # for displaying frame rate
        screen.blit(fps, (50, 50))

        pygame.display.update()
        clock.tick(30)  # for frame rate


def final_scores():
    main_menu_button = create_button("MAIN MENU", 835, 775, 250, 75, main_menu)
    button_list = [main_menu_button]

    results = [Tile(letter) for letter in "RESULTS"]

    global done, totally_done
    done = False
    while not done and not totally_done:
        keys = pygame.key.get_pressed()
        screen.blit(background_empty, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT or keys[pygame.K_ESCAPE]:
                totally_done = True  # if you quit the program, end the whole thing

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for button in button_list:
                    if button["rect"].collidepoint(event.pos[0], event.pos[1]):
                        button["callback"]()

            elif event.type == pygame.MOUSEMOTION:
                # When the mouse gets moved, change the color of the buttons if they collide with the mouse.
                for button in button_list:
                    if button['rect'].collidepoint(event.pos[0], event.pos[1]):
                        button['color'] = active_color
                    else:
                        button['color'] = inactive_color

        # "RESULTS" in tiles
        for idx, letter in enumerate(results):
            screen.blit(pygame.transform.scale(letter.image, (140, 140)),
                        (415+158*idx, 210))

        # blue rectangles, names, and scores
        for rect in [p1_name_rect_final, p1_score_rect_final, p2_name_rect_final, p2_score_rect_final]:
            pygame.draw.rect(screen, tile_blue, rect)

        screen.blit(p1_name_text_final, (520, 461))
        screen.blit(p2_name_text_final, (520, 601))

        p1_score_text_final = futura_final_scores.render(str(p1_score), True, white)
        p2_score_text_final = futura_final_scores.render(str(p2_score), True, white)
        p1_final_score_rect = p1_score_text_final.get_rect(top=452, right=1407)
        p2_final_score_rect = p2_score_text_final.get_rect(top=592, right=1407)
        screen.blit(p1_score_text_final, p1_final_score_rect)
        screen.blit(p2_score_text_final, p2_final_score_rect)

        # main menu button
        draw_button(main_menu_button)

        fps = futura.render(str(int(clock.get_fps())), True, white)  # for displaying frame rate
        screen.blit(fps, (50, 50))

        pygame.display.update()
        clock.tick(30)  # for frame rate


def main_menu():
    short_game_button = create_button("SHORT GAME (7)", 335, 455, 350, 75, short_game)
    medium_game_button = create_button("MEDIUM GAME (11)", 785, 455, 350, 75, medium_game)
    long_game_button = create_button("LONG GAME (15)", 1235, 455, 350, 75, long_game)
    letters_button = create_button("LETTERS", 335, 605, 350, 75, letters_practice)
    numbers_button = create_button("NUMBERS", 785, 605, 350, 75, numbers_practice)
    conundrum_button = create_button("CONUNDRUMS", 1235, 605, 350, 75, conundrum_practice)
    quit_game_button = create_button("QUIT", 835, 755, 250, 75, quit_game)
    button_list = [short_game_button, medium_game_button, long_game_button, letters_button, numbers_button,
                   conundrum_button, quit_game_button]

    reset_letters()

    countdown_title = [Tile(letter) for letter in "COUNTDOWN"]

    pygame.mixer.music.load("Music/Countdown Theme Remix.mp3")
    pygame.mixer.music.play(-1)

    global p1_score, p2_score
    p1_score, p2_score = 0, 0

    global intro, totally_done
    intro = True
    while intro and not totally_done:
        keys = pygame.key.get_pressed()
        screen.blit(background_empty, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT or keys[pygame.K_ESCAPE]:
                totally_done = True  # if you quit the program, end the whole thing

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for button in button_list:
                    if button["rect"].collidepoint(event.pos[0], event.pos[1]):
                        button["callback"]()

            elif event.type == pygame.MOUSEMOTION:
                # When the mouse gets moved, change the color of the buttons if they collide with the mouse.
                for button in button_list:
                    if button['rect'].collidepoint(event.pos[0], event.pos[1]):
                        button['color'] = active_color
                    else:
                        button['color'] = inactive_color

        # "COUNTDOWN" in tiles
        for idx, letter in enumerate(countdown_title):
            screen.blit(pygame.transform.scale(letter.image, (140, 140)),
                        (257+158*idx, 210))

        # draw buttons
        for button in button_list:
            draw_button(button)

        fps = futura.render(str(int(clock.get_fps())), True, white)  # for displaying frame rate
        screen.blit(fps, (50, 50))

        pygame.display.update()
        clock.tick(30)  # for frame rate


def short_game():  # play a short game of 7 rounds
    letters_game()
    letters_game()
    numbers_game()
    letters_game()
    letters_game()
    numbers_game()
    conundrum()
    while p1_score == p2_score and not totally_done:  # if the scores are still tied, load another conundrum
        conundrum()
    final_scores()


def medium_game():  # play a medium game of 11 rounds
    letters_game()
    letters_game()
    numbers_game()
    letters_game()
    numbers_game()
    letters_game()
    letters_game()
    numbers_game()
    letters_game()
    numbers_game()
    conundrum()
    while p1_score == p2_score and not totally_done:  # if the scores are still tied, load another conundrum
        conundrum()
    final_scores()


def long_game():  # play a long (full standard) game of 15 rounds
    letters_game()
    letters_game()
    numbers_game()
    letters_game()
    letters_game()
    numbers_game()
    letters_game()
    letters_game()
    numbers_game()
    letters_game()
    letters_game()
    letters_game()
    letters_game()
    numbers_game()
    conundrum()
    while p1_score == p2_score and not totally_done:  # if the scores are still tied, load another conundrum
        conundrum()
    final_scores()


def letters_practice():  # play 5 letters games
    for i in range(5):
        letters_game()
        reset_letters()
    main_menu()


def numbers_practice():  # play 5 numbers games
    for i in range(5):
        numbers_game()
    main_menu()


def conundrum_practice():  # play 5 conundrums
    for i in range(5):
        conundrum()
    main_menu()


def game_test():  # for testing
    main_menu()
    numbers_game()
    letters_game()
    conundrum()
    while p1_score == p2_score and not totally_done:  # if the scores are still tied, load another conundrum
        conundrum()
    final_scores()


main_menu()

pygame.quit()
