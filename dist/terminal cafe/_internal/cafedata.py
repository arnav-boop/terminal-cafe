itemsfromthemenu = {
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
itemprice = {
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
preptimeforitem = {
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
category = {k: ("drink" if int(k) <= 9 else "edible") for k in itemsfromthemenu}
customers = ["Nona", "Pearl", "Bitten", "Bite", "Groot", "Moss", "Tiggy",     # [P2] new
                  "Juno", "Pipe", "Rock", "Echoes", "Mango", "Wafflemaker", "Chloe", "Dota", "Fizz"]
customerlabels = "abcdefghijklmnoprstuvwxyz"            # the keys you press; no q (quit)

#art
steamframes = [
    [r"      ) (", r"     ( ) )", r"    ) ( ("],
    [r"      ( )", r"      ) ( (", r"     ( ) )"],
]
cupascii = [
    r"  (_______)_",
    r" .-'---------|",
    r"( C|/\/\/\/\/|",
    r" '-./\/\/\/\/|",
    r"  '_________'",
    r"   '-------'",
]
pizzaascii = [
   "EDIBLES: ",  
    "",
    r'//""--.._',
    r'|| (_) _ "-._',
    r"|| _ (_) '-.",
    r"|| (_) __..-'",
    r' \\__..--""',
    "",
]
cookingloader = "|/-\\"                                                 # [P2] new

highscore = 0








