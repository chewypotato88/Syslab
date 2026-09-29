import sys; args = sys.argv[1:]
import re, time, math

import os, copy

global ALPHABET
global STARS
global DEFB
STARS = [60, 60 + 6, 60 + 12, 9 * 19 + 3, 9 * 19 + 9, 9 * 19 + 15, 15 * 19 + 3, 15 * 19 + 9, 15 * 19 + 15]
ALPHABET = "abcdefghijklmnopqrstuvwxyz"
DEFB = [0] * 19 ** 2

def main():
    path = args[0]
    # flist = parseList([f for (r, d, f) in os.walk(path)])
    # print(f"{len(flist)} files found")
    # parse = []
    # for f in flist:
    #     if f.endswith(".sgf"):
    #         parse.append(f)
    parse = readFiles(path)

    print(f"{len(parse)} sgf files found")
    # PARSE RAW .SGF FORMAT AND CONVERT INTO A LIST OF MOVES IN THE FORM OF ["ab", "cd", "PASS", ..., "rs"]
    with open("train.csv", "w") as file: 
        file.write(",".join([str(i) for i in range(19 ** 2)] + ["move"]) + "\n")
    with open("test.csv", "w") as file: 
        file.write(",".join([str(i) for i in range(19 ** 2)] + ["move"]) + "\n")
    split = round(len(parse) * 0.8)
    print("Parsing...")
    for p in parse[:split]:
        parseGame(p, "train.csv")
    for p in parse[split:]:
        parseGame(p, "test.csv")

def readFiles(path):
    fls = []
    for entry in os.listdir(path):
        fullPath = os.path.join(path, entry)
        if os.path.isdir(fullPath): fls = fls + readFiles(fullPath)
        elif fullPath.endswith(".sgf"): fls.append(fullPath)
    return fls

def parseGame(arg, output):
    with open(arg, "r", encoding = "utf-8") as file:
        prev = None
        moves = []
        try:
            text = file.read().split(";")
        except:
            print(f"FAILED TO WRITE {arg}; INVALID CHARACTERS")
            return
        for t in text:
            if (a := re.match("^(W|B)\\[[a-s][a-s]\\]", t)): 
                if prev == a[0][0]:
                    moves.append("PASS")
                moves.append(a[0][2:-1])
                prev = a[0][0]

    # CONVERT MOVES INTO BOARDSTATES AND APPEND TO .CSV
    states = []
    plr = -1
    for i, m in enumerate(moves):
        #print(i, m)
        if m == "PASS":
            if i == 0:
                states.append((DEFB, -100))
            else:
                bd = copy.deepcopy(states[-1][0])
                if bd[states[-1][1]] != "PASS":
                    bd[states[-1][1]] = [p for p in [plr]][0]
                states.append((bd, -100))
        elif i == 0:
            states.append((DEFB, convertMove(m)))
        else: 
            bd = copy.deepcopy(states[-1][0])
            if bd[states[-1][1]] != "PASS":
                bd[states[-1][1]] = [p for p in [plr]][0]
                bd = clearDead(bd, states[-1][1], plr)
            states.append((bd, convertMove(m)))
        plr *= -1

    # PRINT BOARDS
    # temp = None
    # for st in states:
    #     showBoard(st[0], temp, 1)
    #     print(st[1])
    #     temp = st[1]

    with open(output, "a") as file:
        p = 1
        for st in states:
            file.write(",".join([str(i * p) for i in st[0]] + [str(st[1])]) + "\n")
            p *= -1

        # print(f"game {arg} written to {output}")

'''
Assume board is a 19x19 matrix of either 1 (black), 0 (empty), or -1 (white)
and is stored as a 361 length string

last is the index of the last move played

lastP is either 1 (black) or -1 (white)
'''

def convertMove(mv):
    return ALPHABET.index(mv[0]) * 19 + ALPHABET.index(mv[1])
def clearDead(board, last, lastP):
    # up
    if last >= 19 and board[last - 19] == -lastP:
        if floodfill(board, last - 19, []):
            board = flooddelete(board, last - 19)
    # down
    if last + 19 < 361 and board[last + 19] == -lastP: 
        if floodfill(board, last + 19, []):
            board = flooddelete(board, last + 19)
    # left
    if last % 19 != 0 and board[last - 1] == -lastP:
        if floodfill(board, last - 1, []):
            board = flooddelete(board, last - 1)
    # right
    if last % 19 != 18 and board[last + 1] == -lastP:
        if floodfill(board, last + 1, []):
            board = flooddelete(board, last + 1)
    return board
def floodfill(board, idx, group):
    if idx in group: return True
    group.append(idx)
    p = [i for i in [board[idx]]][0]
    u, d, l, r = True, True, True, True
    # up
    if idx >= 19:
        if board[idx - 19] == 0: return False
        if board[idx - 19] == p:
            u = floodfill(board, idx - 19, group)
    # down
    if idx + 19 < 361: 
        if board[idx + 19] == 0: return False
        if board[idx + 19] == p:
            d = floodfill(board, idx + 19, group)
    # left
    if idx % 19 != 0:
        if board[idx - 1] == 0: return False
        if board[idx - 1] == p:
            l = floodfill(board, idx - 1, group)
    # right
    if idx % 19 != 18:
        if board[idx + 1] == 0: return False
        if board[idx + 1] == p:
            r = floodfill(board, idx + 1, group)
    return u and d and l and r
def flooddelete(board, idx):
    p = [i for i in [board[idx]]][0]
    board[idx] = 0
    # up
    if idx >= 19 and board[idx - 19] == p:
        board = flooddelete(board, idx - 19)
    # down
    if idx + 19 < 361 and board[idx + 19] == p: 
        board = flooddelete(board, idx + 19)
    # left
    if idx % 19 != 0 and board[idx - 1] == p:
        board = flooddelete(board, idx - 1)
    # right
    if idx % 19 != 18 and board[idx + 1] == p:
        board = flooddelete(board, idx + 1)
    return board

def showBoard(board, lst, style):
    if lst == None: lst = -1
    if style == 0: 
        for i in range(19):
            print(" ".join([(("." if j + i * 19 not in STARS else "*") if v == 0 else (("b" if j + i * 19 != lst else "B") if v == 1 else ("w" if j + i * 19 != lst else "W"))) for j, v in enumerate(board[i * 19:i * 19 + 19])]))
        print()
    elif style == 1:
        for i in range(19):
            print(" ".join([(("." if j + i * 19 not in STARS else "*") if v == 0 else (("+" if j + i * 19 != lst else "X") if v == 1 else ("-" if j + i * 19 != lst else "O"))) for j, v in enumerate(board[i * 19:i * 19 + 19])]))
        print()

if __name__ == "__main__": main()