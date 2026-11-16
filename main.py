import random
import time
import msvcrt
import math
import sys
import os
import winsound
import threading

from cafedata import *

TOTAL_DAYS = 7
START_MONEY = 150
START_STOCK = 6
SPECIAL_DISCSNT = 0.7
ART_W = 24
L_PANEL_W = 84
DAY_SECONDS = 90
AVG_CUST_DELAY = 6.0
MAX_CUSTS = 12
DEFAULT_PATIENCE = 45

ansiuseable = True
frameCounter = 0

highscore = 0 # global

def load_hi():
    fn = "highscore.txt"
    if not os.path.exists(fn):
        return 0
        
    f = open(fn, "r")
    data = f.read()
    f.close()
    
    try:
        return int(data)
    except:
        return 0

def save_hi(s):
    try:
        old = load_hi()
        if s > old:
            f = open("highscore.txt", "w")
            f.write(str(s))
            f.close()
    except:
        pass

def startday(c):
    c['elapsed'] = 0.0
    c['customers'] = []
    c['log'] = []
    c['served'] = 0
    c['walked'] = 0
    c['revenue'] = 0
    c['specialitems'] = random.choice(list(itemsfromthemenu.keys()))
    c['rushtimer'] = 0.0
    c['critic'] = False
    c['eventtriggered'] = False
    c['chef_msg'] = ""
    c['chef_timer'] = 10.0
    c['auto_cooldown'] = 30.0 # auto chef needs a break sometimes

def setupcafe():
    d = {}
    d['money'] = START_MONEY
    d['stock'] = {}
    d['day'] = 1
    d['rep'] = 50
    d['prices'] = itemprice.copy()
    d['specialitems'] = None
    d['cooks'] = 2
    
    for k in itemsfromthemenu:
        d['stock'][k] = START_STOCK
        
    startday(d)
    return d

def busycooks(cafeRef):
    cnt = 0
    for cust in cafeRef['customers']:
        if cust['state'] == 'cooking':
            cnt += 1
    return cnt

def startcooking(cafeData, targetLabel):
    for c in cafeData['customers']:
        if c['label'] == targetLabel:
            if c['state'] == 'cooking': 
                return 'this order is already cooking'
                
            if busycooks(cafeData) >= cafeData['cooks']: 
                return 'no free cook right now!'
                
            # check stock
            x = 0
            for item in c['items']:
                if cafeData['stock'].get(item, 0) <= 0:
                    return "out of " + itemsfromthemenu[item] + "!"
                else:
                    x = x + 1
            
            # deduct stock
            for item in c['items']:
                cafeData['stock'][item] -= 1

            c['state'] = 'cooking'
            c['cookleft'] = float(c['prep'])
            return ''
    return ''

def say(cRef, msg):
    cRef['log'].append(msg)
    while len(cRef['log']) > 3:
        cRef['log'].pop(0)

def serve(cDict, cObj):
    p = cObj['price']
    cDict['money'] += p
    cDict['revenue'] = cDict['revenue'] + p
    cDict['served'] += 1
    cDict['rep'] = min(100, cDict['rep'] + 1)
    cDict['customers'].remove(cObj)
    
    say(cDict, cObj['name'] + " paid " + str(p) + " sand grains!")

def arrivalrate(c):
    a = 1 / AVG_CUST_DELAY
    b = 0.5 + c['rep'] / 100
    return a * b

def freelabel(cafeDict):
    used = []
    for c in cafeDict['customers']:
        used.append(c['label'])
        
    for ltr in customerlabels:
        if ltr not in used:
            return ltr
            
    return None

def walkout(cafe, cust):
    cafe['rep'] = max(0, cafe['rep'] - 4)
    cafe['walked'] = cafe['walked'] + 1
    cafe['customers'].remove(cust)
    say(cafe, "%s got tired of waiting and left! :(" % cust['name'])

def do_event(cafe):
    r = random.randint(1, 2)
    if r == 1:
        say(cafe, "event: rush hour! customers are flooding in!")
        cafe['rushtimer'] = 15.0
    else:
        say(cafe, "event: food critic visiting today! rep changes are doubled!")
        cafe['critic'] = True

def step(cafe, dt):
    cafe['elapsed'] += dt

    if cafe['chef_timer'] > 0:
        cafe['chef_timer'] -= dt
        
    if cafe['auto_cooldown'] > 0:
        cafe['auto_cooldown'] -= dt

    # trigger event
    if cafe['elapsed'] >= 40:
        if cafe['elapsed'] <= 45:
            if cafe['eventtriggered'] == False:
                cafe['eventtriggered'] = True
                do_event(cafe)

    # rush hour
    mult = 1.0
    if cafe['rushtimer'] > 0:
        mult = 2.0
        cafe['rushtimer'] -= dt

    if cafe['elapsed'] < DAY_SECONDS - 12:
        if random.random() < (arrivalrate(cafe) * mult) * dt:
            spawncust(cafe)

    autochef(cafe)

    temp_l = list(cafe['customers'])
    for c in temp_l:
        c['patienceleft'] -= dt
        
        if c['state'] == 'cooking':
            c['cookleft'] -= dt
            if c['cookleft'] <= 0:
                serve(cafe, c)
                continue
                
        if c['patienceleft'] <= 0:
            walkout(cafe, c)

def priceof(cafe, item):
    p = cafe['prices'][item]
    if cafe['specialitems'] == item:
        p = int(p * SPECIAL_DISCSNT)
    return p

def spawncust(cafe):
    if len(cafe['customers']) >= MAX_CUSTS: 
        return
        
    lbl = freelabel(cafe)
    if lbl == None: 
        return

    avail = []
    for k in cafe['stock']:
        if cafe['stock'][k] > 0:
            avail.append(k)
            
    if not avail:
        return

    sz = random.randint(1, 3)
    chosen = []
    for i in range(sz):
        chosen.append(random.choice(avail))

    tp = 0
    tprep = 0
    for it in chosen:
        tp = tp + priceof(cafe, it)
        tprep += preptimeforitem[it]
        
    nm = random.choice(customers)

    nc = {
        'label': lbl,
        'name': nm,
        'items': chosen,
        'patiencemax': DEFAULT_PATIENCE,
        'patienceleft': DEFAULT_PATIENCE,
        'price': tp,
        'prep': tprep,
        'state': 'waiting',
        'cookleft': 0.0
    }
    cafe['customers'].append(nc)

def itemline(cafe, k):
    nm = itemsfromthemenu[k]
    cst = priceof(cafe, k)
    stk = cafe['stock'][k]
    
    s = "|" + k + ". " + nm + " - " + str(cst) + " sand grains  x" + str(stk)
    if stk == 0:
        s += " [sold out]"
        
    if cafe['specialitems'] == k:
        s += " *special*"
        
    return s

def buildmenuleft(c):
    lines = [" welcome to the terminal cafe!!", "", " drinks:", ""]
    
    idx = (frameCounter // 15) % len(steamframes)
    art = steamframes[idx] + cupascii

    bev = []
    for k in itemsfromthemenu:
        if int(k) <= 9:
            bev.append(k)
    bev.sort(key=int)

    for i in range(len(bev)):
        a = ""
        if i < len(art):
            a = art[i]
        lines.append(a.ljust(ART_W) + itemline(c, bev[i]))

    lines.extend(["", ""])
    
    meals = []
    for item in itemsfromthemenu:
        if int(item) > 9:
            meals.append(item)
    meals.sort(key=int)

    for i in range(len(meals)):
        pic = ""
        if i < len(pizzaascii):
            pic = pizzaascii[i]
        lines.append(pic.ljust(ART_W) + itemline(c, meals[i]))

    return lines

def customerrow(cust):
    if cust['state'] == 'waiting':
        st = 'waiting'
    else:
        sp = cookingloader[frameCounter % len(cookingloader)]
        st = sp + " " + str(math.ceil(cust['cookleft'])) + "s"

    rt = cust['patienceleft'] / cust['patiencemax']
    bl = int((10 * rt) + 0.5)
    
    if bl < 0: 
        bl = 0
    elif bl > 10: 
        bl = 10
        
    # make the meter
    mtr = ".........."
    for i in range(bl):
        mtr = mtr[:i] + "#" + mtr[i+1:]

    items_arr = []
    for x in cust['items']:
        items_arr.append(itemsfromthemenu[x])
    
    n_str = ""
    for y in range(len(items_arr)):
        n_str += items_arr[y]
        if y < len(items_arr) - 1:
            n_str += ", "
        
    if len(n_str) > 20:
        n_str = n_str[:17] + "..." 

    p1 = "[" + cust['label'] + "] "
    p2 = cust['name'].ljust(12) + " "
    p3 = st.ljust(9) + " "
    p4 = n_str.ljust(20) + "   "
    
    return p1 + p2 + p3 + p4 + mtr

def draw(cafe):
    global frameCounter
    frameCounter += 1

    sys.stdout.write("\033[2J\033[1;1H")
    
    L = buildmenuleft(cafe)
    R = ["customers:     status:   items:                   patience:  ", ""]

    for m in cafe['log']:
        R.append(" > " + m)
        
    while len(R) < 5:
        R.append("")

    for cust in cafe['customers']:
        R.append(customerrow(cust))

    max_l = len(L)
    if len(R) > max_l: 
        max_l = len(R)
    
    for i in range(max_l):
        l_str = ""
        r_str = ""
        if i < len(L): l_str = L[i]
        if i < len(R): r_str = R[i]
        
        print(l_str.ljust(L_PANEL_W) + " | " + r_str)

    print("")
    print("day: " + str(cafe['day']) + "  sand grains: " + str(cafe['money']) + "  rep: " + str(cafe['rep']) + "/100")
    print("press the order letter to cook, space to pause, q to quit.")
    
    # indicators
    if cafe['chef_timer'] > 0:
        print("  >> " + cafe['chef_msg'] + " <<")
    else:
        if busycooks(cafe) < cafe['cooks']:
            wait_count = 0
            for c in cafe['customers']:
                if c['state'] == 'waiting':
                    wait_count += 1
                    
            if wait_count > 0:
                if cafe['auto_cooldown'] > 0:
                    print("  >> auto-chef is resting (" + str(round(cafe['auto_cooldown'], 1)) + "s). your turn to cook! <<")
                else:
                    print("  >> [action] cooks are free! press a letter to cook! <<")
                
    sys.stdout.flush()

def pollkey():
    if not msvcrt.kbhit():
        return None
    k = msvcrt.getch()
    if k in (b"\x00", b"\xe0"):
        msvcrt.getch()
        return None
    return k.decode("utf-8", errors="ignore").lower()

def closingtime(cafe):
    for c in list(cafe['customers']):
        cafe['rep'] = max(0, cafe['rep'] - 1)
        cafe['walked'] += 1
        say(cafe, c['name'] + " had to leave as the cafe closed")
    cafe['customers'] = []

def autochef(cafe):
    if cafe['auto_cooldown'] > 0:
        return
        
    tried_labels = []

    while True:
        if busycooks(cafe) >= cafe['cooks']:
            break
            
        target = None
        low = 9999
        for c in cafe['customers']:
            if c['state'] == 'waiting':
                if c['label'] in tried_labels:
                    continue
                    
                if c['patienceleft'] < low:
                    low = c['patienceleft']
                    target = c
                    
        if target == None:
            break
            
        result = startcooking(cafe, target['label'])
        
        if result != "":
            tried_labels.append(target['label'])
        else:
            cafe['chef_msg'] = "auto-chef cooked " + target['name'] + "'s order!"
            cafe['chef_timer'] = 2.0
            cafe['auto_cooldown'] = 4.0 # 4 second break
            break 

def runday(cafe):
    p_flag = False
    prevTime = time.time()

    while cafe['elapsed'] < DAY_SECONDS:
        curTime = time.time()
        deltaT = curTime - prevTime
        prevTime = curTime

        if deltaT > 0.5:
            deltaT = 0.5

        keyInput = pollkey()
        
        if keyInput == 'q':
            return 'quit'
        elif keyInput == ' ':
            if p_flag == False:
                p_flag = True
            else:
                p_flag = False
        elif keyInput and p_flag == False:
            res = startcooking(cafe, keyInput)
            if res: 
                say(cafe, res)
            else:
                cafe['chef_msg'] = "you manually started cooking!"
                cafe['chef_timer'] = 2.0

        if p_flag == False:
            step(cafe, deltaT)

        draw(cafe)
        time.sleep(0.05)

    closingtime(cafe)
    draw(cafe)
    time.sleep(1.0)

    return 'done'

def nightshop(cafe):
    print("\n" * 500)
    print("========================================")
    print("        end of day " + str(cafe['day']) + " summary")
    print("========================================")
    print(" customers served      :  " + str(cafe['served']))
    print(" customers walked out  :  " + str(cafe['walked']))
    print(" today's revenue       :  " + str(cafe['revenue']) + " sand grains")
    print(" total money           :  " + str(cafe['money']) + " sand grains")
    print(" reputation            :  " + str(cafe['rep']) + "/100")
    print("----------------------------------------")

    print(" spoilage report:")
    for k in cafe['stock']:
        sp = math.floor(cafe['stock'][k] * 0.3)
        cafe['stock'][k] -= sp
        if sp > 0:
            print(" - " + itemsfromthemenu[k] + ": " + str(sp) + " lost to spoilage")

    rent = 100 + 100 * (cafe['day'] - 1)
    cafe['money'] -= rent
    print("----------------------------------------")
    print(" rent paid             : " + str(rent) + " sand grains")
    print(" balance after rent    : " + str(cafe['money']) + " sand grains")
    print("========================================")

    if cafe['money'] < 0:
        print("\n magga you went bankrupt! game over.")
        return "bankrupt"
        
    if cafe['rep'] <= 0:
        print("\n deiii your shop's rep hit the floor! game over.")
        return "bankrupt"

    if cafe['day'] == TOTAL_DAYS:
        return "victory"

    input("\n press enter to open nightshop and restock...")

    while True:
        print("\n---- night supplies shop ----")
        print("your money: " + str(cafe['money']) + " sand grains")
        print("1. buy stock (costs 60% of base price)")
        print("2. hire extra cook (cost: 300) [current cooks: " + str(cafe['cooks']) + "]")
        print("3. adjust menu prices (markup multiplier)")
        print("4. continue to next day")
        choice = input("select option (1-4): ").strip()

        if choice == '1':
            print("\nmenu items:")
            for k, name in itemsfromthemenu.items():
                cost = round(itemprice[k] * 0.6)
                print("[" + str(k) + "] " + name + " - " + str(cost) + " sand grains (stock: " + str(cafe['stock'][k]) + ")")
                
            item_choice = input("enter item number to buy (or enter to go back): ").strip()
            
            if item_choice in cafe['stock']:
                cost = round(itemprice[item_choice] * 0.6)
                qty_str = input("how many " + itemsfromthemenu[item_choice] + "s to buy? ").strip()
                
                if qty_str.isdigit():
                    qty = int(qty_str)
                    total_cost = cost * qty
                    if cafe['money'] >= total_cost:
                        cafe['money'] = cafe['money'] - total_cost
                        cafe['stock'][item_choice] += qty
                        print("bought " + str(qty) + " " + itemsfromthemenu[item_choice] + "!")
                    else:
                        print("not enough sand grains!")
            time.sleep(1.0)

        elif choice == '2':
            cook_cost = 300
            if cafe['money'] >= cook_cost:
                cafe['money'] -= cook_cost
                cafe['cooks'] += 1
                print("hired an extra cook! total cooks: " + str(cafe['cooks']))
            else:
                print("not enough sand grains to hire a cook!")
            time.sleep(1.0)

        elif choice == '3':
            print("\n--- price adjustment ---")
            print("enter new price multiplier (e.g. 1.0 for normal, 1.2 for 20% higher, 0.8 for discount):")
            mult_str = input("multiplier (0.6 to 1.5): ").strip()
            try:
                mult = float(mult_str)
                if mult >= 0.6 and mult <= 1.5:
                    for k in cafe['prices']:
                        cafe['prices'][k] = round(itemprice[k] * mult)
                    print("prices updated with multiplier " + str(mult) + "x!")
                else:
                    print("multiplier must be between 0.6 and 1.5!")
            except ValueError:
                print("invalid number!")
            time.sleep(1.0)

        elif choice == '4':
            break
        else:
            print("invalid choice") 
            time.sleep(0.5)

    return "continue"

def play_sfx(f, d):
    def run():
        try:
            winsound.Beep(f, d)
        except RuntimeError:
            pass
    t = threading.Thread(target=run)
    t.daemon = True
    t.start()

def titlescreen(ch):
    while True:
        print("\n" * 50)
        print("=========================================")
        print("          the terminal cafe              ")
        print("=========================================")
        print(" current high score : " + str(ch) + " sand grains")
        print("-----------------------------------------")
        print(" [s] start game")
        print(" [q] quit")
        print("=========================================")
        choice = input("select option: ").lower().strip() 
        
        if choice == 's':
            play_sfx(1000, 150)
            break
        elif choice == 'q':
            sys.exit(0)
        else:
            print("wrong key")
            time.sleep(0.5)

def game():
    global highscore
    highscore = load_hi()
    
    # random debug variable
    debug_mode = False

    titlescreen(highscore)

    c = setupcafe()
    c['specialitems'] = '3'

    while c['day'] <= TOTAL_DAYS:
        out = runday(c)
        
        if out == 'quit': 
            sys.exit(0)

        print('\nday finished!')
        print('customers served: ' + str(c['served']))
        print('customers walked out: ' + str(c['walked']))
        print("today's revenue: " + str(c['revenue']))
        print('total money: ' + str(c['money']))

        input('\npress enter to see the night summary...')

        res = nightshop(c)
        
        if res == "bankrupt":
            play_sfx(200, 400)
            break
            
        if res == "victory":
            play_sfx(1200, 300)
            print('\nyou survived 7 days! victory!!')
            break

        c['day'] += 1
        startday(c)

    save_hi(c['money'])
    
    print("\nfinal score: " + str(c['money']) + " sand grains")
    print('\nthanks for playing terminal cafe!, nandri vanakkam')

if __name__ == '__main__':
    try:
        game()
    except KeyboardInterrupt:
        print("game stopped.")