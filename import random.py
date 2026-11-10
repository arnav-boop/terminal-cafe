import random
import time
import msvcrt 
from cafedata import MENU_NAMES, MENU_PREP, BASE_PRICES, CATEGORY, CUSTOMER_NAMES, LABELS, STEAM, CUP, FOOD_ART, SPINNER, highscore
from collections import deque


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
        self.start_day()           

    def arrivalrate(self):
        base =  1 / BASE_INTERVAL
        factor = 0.5 + self.rep / 100
        return(base * factor)   

    def freelabel(self):
        used = {c.label for c in self.customers}
        for letters in LABELS:
            if letters not in used:
                return letters

        return None

    def say(self, text):
        self.log.append(text)

    def walkout(self, c):
        self.rep = max(0, self.rep - 4)      # max keeps rep from going below 0
        self.walked += 1                   # one more customer lost
        self.customers.remove(c)
        self.say(f"{c.name} got tired of waiting and left!")

    def step(self, dt):
        self.elapsed += dt
    # 1. maybe a customer arrives
        if self.elapsed < DAY_SECONDS - 12 and random.random() < self.arrivalrate() * dt:       # dice roll from idea 2
            self.spawncust()
    # 2. patience drains for everyone
        for c in list(self.customers):
             c.patience_left -= dt
             if c.patience_left <= 0:                                       # patience has run out
                 self.walkout(c)

    def popularity(self,key):
        return((25/ BASE_PRICES[key]) ** 0.5)

    def spawncust(self):
        label = self.freelabel()
        if label is None or len(self.customers) >= MAX_CUSTOMER:
            return
        count = random.choices([1,2,3], weights=[5,4,1])[0]
        keys = list(MENU_NAMES)
        weights = [self.popularity(key) for key in keys]
        items = random.choices(keys, weights=weights, k=count)
        price = sum(self.priceof(k) for k in items)
        prep = sum(MENU_PREP[k] for k in items)
        name = random.choice(CUSTOMER_NAMES)
        self.customers.append(Customer(label, name, items, BASE_PATIENCE, price, prep))


    def priceof(self, key):
        if self.specialitems == key:
            return(round(self.prices[key] * SPECIAL_DISCOUNT))
        return(self.prices[key])

    def start_day(self):
        self.elapsed = 0.0
        self.customers = []
        self.log = deque(maxlen=3)
        self.served = 0
        self.walked = 0
        self.revenue = 0




def itemline(cafe, key):
    text = f"|{key}. {MENU_NAMES[key]} - {cafe.priceof(key)} Sand Grains  x{cafe.stock[key]}"
    if cafe.stock[key] == 0:                      # stock for this key is 0
        text += " [SOLD OUT]"
    if cafe.specialitems == key:                      # this key is the special
        text += " *SPECIAL*"
    return(text)

def draw(cafe):
    global frame
    frame += 1
    print("\n"* 1000)

    for line in build_menu_left(cafe):
        print(line)
    print("")
    print(f"day: {cafe.day}  sand grains: {cafe.money} rep: {cafe.rep}/100")
    print("ctrl c to stop")

def build_menu_left(cafe):
    lines = [" WELCOME TO THE TERMINAL CAFE!!", "", " DRINKS:", ""]

    drink_art = STEAM[frame % 2] +  CUP                 # steam picture plus CUP
    drinks = sorted((n for n in MENU_NAMES if int(n) <= 9), key=int)        # keys whose CATEGORY is "drink"
    for i, key in enumerate(drinks):
        art = drink_art[i] if i < len(drink_art) else ""                            # drink_art[i], or "" if i is too big
        lines.append(art.ljust(ART_W) + itemline(cafe, key))
    # now do the same for edibles, with FOOD_ART
    food_art = FOOD_ART
    lines += ["", ""]
    food = sorted((n for n in MENU_NAMES if int(n) > 9), key = int) 
    for i, key in enumerate(food):
        art = food_art[i] if i < len(food_art) else ""
        lines.append(art.ljust(ART_W) + itemline(cafe, key))
    return lines

class Customer:
    def __init__(self, label, name, items, patience, price, prep):
        self.patience_max = patience
        self.patience_left = patience
        self.label = label
        self.name = name
        self.items = items
        self.prep = prep
        self.price = price
        self.state = "waiting"
        self.cook_left = 0.0


def test():
    cafe = Cafe()
    for _ in range(360):          # 360 ticks x 0.25 seconds = 90 seconds
        cafe.step(0.25)
    print(cafe.elapsed, len(cafe.customers), cafe.walked, cafe.rep)
    print(list(cafe.log))

def game():
    print("welcome to the terminal cafe!!")
    print(f"The current high score is {highscore}")
    cafe = Cafe()

    cafe.stock["1"] = 0
    cafe.specialitems = "3"

    try:
        while True:
            draw(cafe)
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\n bye!!")


if __name__ == "__main__":
    test()

