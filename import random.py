import random
import time
import msvcrt 
from cafedata import MENU_NAMES, MENU_PREP, BASE_PRICES, CATEGORY, CUSTOMER_NAMES, LABELS, STEAM, CUP, FOOD_ART, SPINNER, highscore

#settings
DAYS = 7
START_MONEY = 150
START_STOCK = 6
SPECIAL_DISCOUNT = 0.7
ART_W = 24
LEFT_W = 84
DAY_SECONDS = 90
BASE_INTERVAL = 6.0
MAX_CUSTOMER = 12
BASE_PATIENCE = 45
USE_ANSI = True
frame = 0 

class Cafe:
    def __init__(self):
        self.money = START_MONEY
        self.stock = {k: START_STOCK for k in MENU_NAMES}
        self.day = 1
        self.rep = 50
        self.prices = dict(BASE_PRICES)
        self.specialitems = None

    def priceof(self, key):
        if self.specialitems == key:
            return(round(self.prices[key] * SPECIAL_DISCOUNT))
        return(self.prices[key])

def itemline(cafe, key):
    text = f"|{key}. {MENU_NAMES[key]} - {cafe.priceof(key)} Sand Grains  x{cafe.stock[key]}"
    if cafe.stock[key] == 0:                      # stock for this key is 0
        text += " [SOLD OUT]"
    if cafe.specialitems == key:                      # this key is the special
        text += " *SPECIAL*"
    return(text)


def build_menu_left(cafe):
    lines = [" WELCOME TO THE TERMINAL CAFE!!", "", " DRINKS:", ""]
    drink_art = STEAM[frame % 2] +  CUP                 # steam picture plus CUP
    drinks = sorted((n for n in MENU_NAMES if n > 2), key=int)            # keys whose CATEGORY is "drink"
    for i, key in enumerate(drinks):
        art = drink_art[art[i] if i < len(art) else ""]                            # drink_art[i], or "" if i is too big
        lines.append(art.ljust(ART_W) + itemline(cafe, key))
    # now do the same for edibles, with FOOD_ART
    return lines

def game():
    print("welcome to the terminal cafe!!")
    print(f"The current high score is {highscore}")
    cafe = Cafe()
    print(cafe.priceof("1"))      # 20
    cafe.specialitems = "1"
    print(cafe.priceof("1"))      # 14
    print(cafe.priceof("2"))      # 30, still normal
    print(BASE_PRICES["1"])       # 20, untouched
    

if __name__ == "__main__":
    game()

