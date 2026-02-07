import pygame
import random
import os

WIDTH, HEIGHT = 900, 600
FPS = 60
GREEN = (34, 139, 34)
WHITE = (255, 255, 255)
GOLD = (255, 215, 0)
BLACK = (0, 0, 0)

CARD_W, CARD_H = 100, 145

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Blackjack MCTS")
font = pygame.font.SysFont('Arial', 24)
big_font = pygame.font.SysFont('Arial', 40)

# GRAFIKA KART
# -----------
card_images = {}

def load_assets():
    suits = ['hearts', 'diamonds', 'clubs', 'spades']
    values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    
    for s in suits:
        for v in values:
            name = f"{v}_of_{s}"
            path = os.path.join('cards', f"{name}.png")
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                card_images[name] = pygame.transform.scale(img, (CARD_W, CARD_H))

    back_path = os.path.join('cards', 'back.png')
    if os.path.exists(back_path):
        back_img = pygame.image.load(back_path).convert_alpha()
        card_images['back'] = pygame.transform.scale(back_img, (CARD_W, CARD_H))
    else:
        surf = pygame.Surface((CARD_W, CARD_H))
        surf.fill((50, 50, 150))
        card_images['back'] = surf

load_assets()

# -----------

def get_value(hand):
    val = 0
    aces = 0
    for card in hand:
        s = card.split('_')[0]
        if s in ['J', 'Q', 'K']: val += 10
        elif s == 'A': val += 11; aces += 1
        else: val += int(s)
    while val > 21 and aces:
        val -= 10
        aces -= 1
    return val

# MCTS
# -----------

def mcts_suggest(player_hand, dealer_up_card, current_deck):
    simulations = 1000
    wins = {'hit': 0, 'stand': 0}
    for move in ['hit', 'stand']:
        for _ in range(simulations):
            sim_deck = list(current_deck)
            random.shuffle(sim_deck)
            sim_player, sim_dealer = list(player_hand), [dealer_up_card]

            if move == 'hit': sim_player.append(sim_deck.pop())
            p_val = get_value(sim_player)
            if p_val > 21: wins[move] -= 1; continue
            # krupier dobiera do 17
            while get_value(sim_dealer) < 17:
                if sim_deck: sim_dealer.append(sim_deck.pop())
                else: break
            d_val = get_value(sim_dealer)
            if d_val > 21 or p_val > d_val: wins[move] += 1
            elif p_val < d_val: wins[move] -= 1
    return "HIT" if wins['hit'] > wins['stand'] else "STAND"

# -----------

class Button:
    def __init__(self, x, y, w, h, text, color):
        self.rect = pygame.Rect(x, y, w, h)
        self.text, self.color = text, color
    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect, border_radius=10)
        txt = font.render(self.text, True, BLACK)
        screen.blit(txt, (self.rect.x + (self.rect.w - txt.get_width())//2, self.rect.y + 10))
    def is_clicked(self, pos): return self.rect.collidepoint(pos)


def game_loop():
    suits = ['hearts', 'diamonds', 'clubs', 'spades']
    values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    deck = [f"{v}_of_{s}" for v in values for s in suits]
    #jak chcemy zwiekszyc liczbe kart jak w kasynie
    #num_decks = 6
    #deck = [f"{v}_of_{s}" for v in values for s in suits] * num_decks
    random.shuffle(deck)
    
    player = [deck.pop(), deck.pop()]
    dealer = [deck.pop(), deck.pop()]
    
    btn_hit = Button(150, 500, 100, 50, "HIT", (100, 255, 100))
    btn_stand = Button(270, 500, 100, 50, "STAND", (255, 100, 100))
    btn_mcts = Button(390, 500, 100, 50, "MCTS", GOLD)
    
    game_over = False
    message = "Twoja tura."
    suggestion = ""

    running = True
    clock = pygame.time.Clock()

    while running:
        screen.fill(GREEN)
        
        for i, card in enumerate(dealer):
            x, y = 50 + i*110, 50
            if i == 1 and not game_over:
                screen.blit(card_images['back'], (x, y))
            else:
                screen.blit(card_images[card], (x, y))

        for i, card in enumerate(player):
            x, y = 50 + i*110, 300
            screen.blit(card_images[card], (x, y))

        btn_hit.draw()
        btn_stand.draw()
        btn_mcts.draw()
        
        msg_surf = font.render(message, True, WHITE)
        screen.blit(msg_surf, (50, 220))
        
        if suggestion:
            sug_surf = big_font.render(f"AI: {suggestion}", True, GOLD)
            screen.blit(sug_surf, (550, 500))

        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                pos = pygame.mouse.get_pos()
                if btn_hit.is_clicked(pos):
                    player.append(deck.pop())
                    if get_value(player) > 21:
                        message = "PRZEGRAŁEŚ! PRZEKROCZYŁEŚ 21!"; game_over = True
                if btn_stand.is_clicked(pos):
                    game_over = True
                    while get_value(dealer) < 17: dealer.append(deck.pop())
                    p_v, d_v = get_value(player), get_value(dealer)
                    if d_v > 21 or p_v > d_v: message = f"WYGRAŁEŚ! Ty: {p_v}, Krupier: {d_v}"
                    elif p_v == d_v: message = "REMIS!"
                    else: message = f"PRZEGRAŁEŚ! Krupier: {d_v}"
                if btn_mcts.is_clicked(pos):
                    suggestion = mcts_suggest(player, dealer[0], deck)
            if event.type == pygame.KEYDOWN and game_over:
                if event.key == pygame.K_SPACE: game_loop()

        pygame.display.flip()
        clock.tick(FPS)

game_loop()
pygame.quit()