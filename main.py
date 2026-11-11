import random
import time
import msvcrt
import math
import sys

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

def startday(c):
    c['elapsed'] = 0.0
    c['customers'] = []
    c['log'] = []
    c['served'] = 0
    c['walked'] = 0
    c['revenue'] = 0

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
    x = 0
    for cust in cafeRef['customers']:
        if cust['state'] == 'cooking':
            x += 1
    return x

def startcooking(cafeData, targetLabel):
    for c in cafeData['customers']:
        if c['label'] == targetLabel:
            if c['state'] == 'cooking': 
                return 'this order is already cooking'
            if busycooks(cafeData) >= cafeData['cooks']: 
                return 'no free cook right now!'
                
            # Check if we have stock for every item in the order
            for item in c['items']:
                if cafeData['stock'].get(item, 0) <= 0:
                    return f"Out of {itemsfromthemenu[item]}!"
            
            # Deduct stock
            for item in c['items']:
                cafeData['stock'][item] -= 1

            c['state'] = 'cooking'
            c['cookleft'] = float(c['prep'])
            return ''
    return ''

def say(cRef, msg):
    cRef['log'].append(msg)
    if len(cRef['log']) > 3: 
        cRef['log'].pop(0)

def serve(cDict, cObj):
    p = cObj['price']
    cDict['money'] += p
    cDict['revenue'] = cDict['revenue'] + p
    cDict['served'] += 1
    cDict['rep'] = min(100, cDict['rep'] + 1)
    cDict['customers'].remove(cObj)
    
    # print("serving " + cObj['name'])
    say(cDict, cObj['name'] + ' paid ' + str(p) + ' sand grains!')

def arrivalrate(c):
    baseRate = 1 / AVG_CUST_DELAY
    repFactor = 0.5 + c['rep'] / 100
    return baseRate * repFactor

def freelabel(cafeDict):
    used_labels = []
    for c in cafeDict['customers']:
        used_labels.append(c['label'])
        
    for ltr in customerlabels:
        if ltr not in used_labels:
            return ltr
            
    return None

def walkout(cafe, cust):
    cafe['rep'] = max(0, cafe['rep'] - 4)
    cafe['walked'] += 1
    cafe['customers'].remove(cust)
    say(cafe, cust['name'] + " got tired of waiting and left! :(")

def step(cafe, dt):
    cafe['elapsed'] += dt
    
    if cafe['elapsed'] < DAY_SECONDS - 12:
        if random.random() < arrivalrate(cafe) * dt:
            spawncust(cafe)

    temp_list = []
    for c in cafe['customers']:
        temp_list.append(c)
        
    for c in temp_list:
        c['patienceleft'] -= dt
        
        if c['state'] == 'cooking':
            c['cookleft'] -= dt
            if c['cookleft'] <= 0:
                serve(cafe, c)
                continue
                
        if c['patienceleft'] <= 0:
            walkout(cafe, c)

def priceof(cafe, item):
    cst = cafe['prices'][item]
    if cafe['specialitems'] == item:
        cst = int(cst * SPECIAL_DISCSNT)
    return cst

def spawncust(cafe):
    if len(cafe['customers']) >= MAX_CUSTS: 
        return
        
    lbl = freelabel(cafe)
    if lbl == None: 
        return

    sz = random.randint(1, 3)
    keys = list(itemsfromthemenu.keys())
    
    chosen = []
    for i in range(sz):
        chosen.append(random.choice(keys))

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
    
    s = '|' + k + '. ' + nm + ' - ' + str(cst) + ' sand Grains  x' + str(stk)
    if stk == 0:
        s += ' [sold out]'
    if cafe['specialitems'] == k:
        s += ' *special*'
        
    return s

def buildmenuleft(c):
    lines = [' welcome to the terminal cafe!!', '', ' drinks:', '']
    
    idx = (frameCounter // 15) % len(steamframes)
    art = steamframes[idx] + cupascii

    bev = []
    for k in itemsfromthemenu:
        if int(k) <= 9:
            bev.append(k)
    bev.sort(key=int)

    for i in range(len(bev)):
        a = ''
        if i < len(art):
            a = art[i]
        lines.append(a.ljust(ART_W) + itemline(c, bev[i]))

    lines.extend(['', ''])
    
    meals = []
    for item in itemsfromthemenu:
        if int(item) > 9:
            meals.append(item)
    meals.sort(key=int)

    for i in range(len(meals)):
        pic = ''
        if i < len(pizzaascii):
            pic = pizzaascii[i]
        lines.append(pic.ljust(ART_W) + itemline(c, meals[i]))

    return lines

def customerrow(cust):
    if cust['state'] == 'waiting':
        st = 'waiting'
    else:
        sp = cookingloader[frameCounter % len(cookingloader)]
        st = sp + ' ' + str(math.ceil(cust['cookleft'])) + 's'

    rt = cust['patienceleft'] / cust['patiencemax']
    bl = int((10 * rt) + 0.5)
    
    if bl < 0: 
        bl = 0
    elif bl > 10: 
        bl = 10
        
    bar_data = ['.'] * 10
    for j in range(bl):
        bar_data[j] = '#'
        
    mtr = ''.join(bar_data)

    items_arr = []
    for x in cust['items']:
        items_arr.append(itemsfromthemenu[x])
    
    n_str = ''
    for y in range(len(items_arr)):
        n_str += items_arr[y]
        if y < len(items_arr) - 1:
            n_str += ', '
        
    if len(n_str) > 20:
        n_str = n_str[:17] + '...' 

    p1 = "[{}] ".format(cust['label'])
    p2 = "%-12s " % cust['name']
    p3 = st.ljust(9) + " "
    p4 = n_str.ljust(20)
    
    final_arr = [p1, p2, p3, p4, "   ", mtr]
    return "".join(final_arr)

def draw(cafe):
    global frameCounter
    frameCounter+=1

    print("\n" * 100, end="")
    L = buildmenuleft(cafe)
    R = ["customers:       status:   items:                 patience:  ", ""]

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

def pollkey():
    if not msvcrt.kbhit():
        return None
    k = msvcrt.getch()
    if k in (b"\x00", b"\xe0"):
        msvcrt.getch()
        return None
    return k.decode("utf-8", errors="ignore").lower()

def runday(cafe):
    paused = 0
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
            if paused == 0:
                paused = 1
            else:
                paused = 0
        elif keyInput and paused == 0:
            res = startcooking(cafe, keyInput)
            if res: 
                say(cafe, res)

        if paused == 0:
            step(cafe, deltaT)

        draw(cafe)
        time.sleep(0.03)

    return 'done'

def game():
    print('welcome to the terminal cafe!!')
    print('the current high score is ' + str(highscore))

    c = setupcafe()
    
    # testing
    c['stock']['1'] = 0
    c['specialitems'] = '3'

    while c['day'] <= TOTAL_DAYS:
        out = runday(c)
        
        if out == 'quit': 
            sys.exit() # changed to sys.exit so it looks weird

        print('\nday finished!')
        print('customers served: ' + str(c['served']))
        print('customers walked out: ' + str(c['walked']))
        print('today\'s revenue: ' + str(c['revenue']))
        print('total money: ' + str(c['money']))

        if c['day'] == TOTAL_DAYS:
            print('\nYOU SURVIVED 7 DAYS! VICTORY!!')
            break

        input('\npress ENTER to start the next day...')
        c['day'] += 1
        startday(c)

    print('\nthanks for playing terminal cafe!, nandri vanakkam')

if __name__ == '__main__':
    try:
        game()
    except KeyboardInterrupt:
        print("Game stopped.")