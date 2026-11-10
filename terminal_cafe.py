import os
import random
import sys
import time
from collections import deque

import msvcrt
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


#menu data
MENU_NAMES = {
    "1": "Coffee",
    "2": "Boba", 
    "3": "Apple Juice", 
    "4": "Milkshake",
    "5": "Vinegar", 
    "6": "Butter Beer", 
    "7": "Cassie's Tears", 
    "8": "Ginger Ale",
    "9": "Guava Juice", 
    "10": "Pizza", 
    "11": "Apple", 
    "12": "Apple Pie",
    "13": "Fries", 
    "14": "Burger", 
    "15": "Waffles", 
    "16": "Cake",
}
BASE_PRICES = {
    "1": 20, 
    "2": 30, 
    "3": 15, 
    "4": 25, 
    "5": 5, 
    "6": 50, 
    "7": 100, 
    "8": 20,
    "9": 15, 
    "10": 50, 
    "11": 5, 
    "12": 20, 
    "13": 15, 
    "14": 50, 
    "15": 30, 
    "16": 25,
}
# seconds one cook needs to make one of each item
MENU_PREP = {
    "1": 4, 
    "2": 5, 
    "3": 2, 
    "4": 5, 
    "5": 1, 
    "6": 6, 
    "7": 10, 
    "8": 2,
    "9": 2, 
    "10": 15, 
    "11": 1, 
    "12": 11, 
    "13": 8, 
    "14": 12, 
    "15": 10, 
    "16": 9,
}
CATEGORY = {k: ("drink" if int(k) <= 9 else "edible") for k in MENU_NAMES}
CUSTOMER_NAMES = ["Nona", "Pearl", "Bitten", "Bite", "Groot", "Moss", "Tiggy",     # [P2] new
                  "Juno", "Pipe", "Rock", "Echoes", "Mango", "Wafflemaker", "Chloe", "Dota", "Fizz"]
LABELS = "abcdefghijklmnoprstuvwxyz"            # the keys you press; no q (quit)

#art
STEAM = [
    [r"    ) (", r"   ( ) )", r"   ) ( ("],
    [r"    ( )", r"   ) ( (", r"   ( ) )"],
]
CUP = [
    r"  (_______)_",
    r" .-'---------|",
    r"( C|/\/\/\/\/|",
    r" '-./\/\/\/\/|",
    r"  '_________'",
    r"   '-------'",
]
FOOD_ART = [
    "",
    r'//""--.._',
    r'|| (_) _ "-._',
    r"|| _ (_) '-.",
    r"|| (_) __..-'",
    r' \\__..--""',
    "",
]
SPINNER = "|/-\\"                                                 # [P2] new
frame = 0                       # counts redraws; used to animate things


#objs

class Customer:
    def __init__(self, label, name, items, patience, price, prep):
        self.label = label
        self.name = name
        self.items = items
        self.patience_max = patience
        self.patience_left = patience
        self.price = price
        self.prep = prep
        self.state = "waiting"
        self.cook_left = 0.0

class Cafe:
    def __init__(self):
        self.day = 1
        self.money = START_MONEY
        self.rep = 50.0
        self.prices = dict(BASE_PRICES)
        self.stock = {k: START_STOCK for k in MENU_NAMES}
        self.special = None
        self.cooks = 3
        self.start_day()

    def price_of(self, key):
        if self.special == key:
            return max(1,round(self.prices[key] * SPECIAL_DISCOUNT))
        return self.prices[key]

    def start_day(self):
        self.elapsed = 0.0
        self.customers = []
        self.log = deque(maxlen=3)
        self.served = 0
        self.walked = 0
        self.revenue = 0

    def say(self, text):
        self.log.append(text)

    def busy_cooks(self):
        return sum(1 for c in self.customers if c.state == "cooking")

    def popularity(self, key):
        return (25 / BASE_PRICES[key] ** 0.5)

    def arrival_rate(self):
        return 


