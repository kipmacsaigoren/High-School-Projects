import random
import time

base32 = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v",
          "w", "x", "y", "z", "1", "2", "3", "4"]
# used to print out the column names on the expert board
digits = [1, 2, 3, 4, 5, 6, 7, 8, 9]
testValue = True
# I shouldn't have to do this.


class difficulty(object):
    # I'm pretty sure the better way to do this would be with a dicitonary,
    # but I dont want to take the time to change it.
    def __init__(self, rows, columns, mines):
        self.rows = rows
        self.columns = columns
        self.total = int(self.rows * self.columns - 1)
        # ^ total number of tiles in the difficulty
        self.mines = mines
        self.flags = mines


easy = difficulty(9, 9, 10)
medium = difficulty(16, 16, 40)
hard = difficulty(16, 30, 99)


def edgeDict(_difficulty):
    """gives you a bunch of lists that tell you which tiles in the list
    are on the edge of the board, which edge, if theyre in the corners,
    and which tiles are in the center."""
    edge = {"left": [], "right": [], "top": [], "bottom": [], "corners": []}
    # the corners one goes 'top-left, top-right, bottom-left, bottom-right'
    for i in range(_difficulty.rows):
        edge["left"].append(i * _difficulty.columns)
    for i in range(_difficulty.rows):
        edge["right"].append(i * _difficulty.columns + _difficulty.columns - 1)
    for i in range(_difficulty.columns):
        edge["top"].append(i)
    for i in range(_difficulty.columns):
        edge["bottom"].append(_difficulty.total - i)
        edge["bottom"].sort()
    edge["corners"].extend([0, _difficulty.columns - 1, (_difficulty.rows - 1) * _difficulty.columns,
                            _difficulty.rows * _difficulty.columns - 1])
    center = []
    for i in range(_difficulty.total):
        if i not in edge["left"] and i not in edge["right"] and i not in edge["top"] and i not in edge["bottom"]:
            center.append(i)
    edge["center"] = center
    return edge


class tile(object):
    def __init__(self, number, visibleValue, value, checked):
        self.number = number
        # ^ location on the board.
        # it could probably be replaced with the list index though. hm.
        # most of the time I actually did just use the index.
        self.visibleValue = visibleValue
        # ^ visibleValue is "[]" if it hasn't been checked,
        # or "F" if flagged
        # or the actual value if checked
        self.value = value
        # ^ can either be a mine, or a number
        self.countDownValue = -1000
        if self.value in digits or self.value == 0:
            self.countDownValue = self.value
        # ^ a value that will countdown when a mine is placed adjacent to it
        # it will let you click on already schecked tiles to sweep around.
        self.checked = checked
        # ^ boolean value

    def check(self):
        if self.value == 0:
            self.checked = True
            self.visibleValue = " "
            # the single splace allows it to print the board correctly.
        elif self.visibleValue == "F ":
            # it stops you from checking flagged tilees?
            # i dont remember why
            # I'm not sure this is even needed. I put a part about checking flagged tiles below
            return
        elif self.value == "M" and testValue == True:
            youDied()
        else:
            self.checked = True
            self.visibleValue = self.value


def SurroundingMines(location, _tilelist, _difficulty):
    # gives each tile a value based on how many mines are immediatly adjacent
    newValue = 0
    hDict = edgeDict(_difficulty)
    # see edgeDict
    # hdict is to indicate that it is a dictionary for a certain hardness
    """Each board is really just a list of tiles.
      This means that I cant just check the 8 tiles adjacent to each tile
      because of tiles on the edge of the board.
      If I did do that, a tile on the right edge of the board would pick up mines
      on the other side of the board.
      so each of these cases ensures a tile is not ot the edge of the board,
      then checs all 8 tiles.
      If it is on an edge of the board, it only checks for mines in the approprite
      surrounding tiles for that edge."""
    if location not in hDict["left"]:
        if _tilelist[location - 1].value == "M":
            newValue += 1
    if location not in hDict["right"]:
        if _tilelist[location + 1].value == "M":
            newValue += 1
    if location not in hDict["left"] and location not in hDict["bottom"]:
        if _tilelist[location + _difficulty.columns - 1].value == "M":
            newValue += 1
    if location not in hDict["bottom"]:
        if _tilelist[location + _difficulty.columns].value == "M":
            newValue += 1
    if location not in hDict["right"] and location not in hDict["bottom"]:
        if _tilelist[location + _difficulty.columns + 1].value == "M":
            newValue += 1
    if location not in hDict["top"]:
        if _tilelist[location - _difficulty.columns].value == "M":
            newValue += 1
    if location not in hDict["top"] and location not in hDict["left"]:
        if _tilelist[location - _difficulty.columns - 1].value == "M":
            newValue += 1
    if location not in hDict["top"] and location not in hDict["right"]:
        if _tilelist[location - _difficulty.columns + 1].value == "M":
            newValue += 1
    return newValue


def boardMaker(_difficulty):
    # each board is really just a list of tile objects
    # This function creates a list populated with mines, number values, and blanks
    # it may not be a solvable board.

    minelist = random.sample(range(_difficulty.total + 1), _difficulty.mines)
    # these locations are where mines will be placed
    tileList = []
    for i in range(_difficulty.total + 1):
        if i in minelist:
            tileList.append(tile(i, [], "M", False))
        else:
            tileList.append(tile(i, [], "", False))
            # leaves tiles that are not mines with blank values.
    for i in range(_difficulty.total + 1):
        # puts the value for the number of surrounding mines into each tile that isn't a mine.
        if tileList[i].value != "M":
            minesAround = SurroundingMines(i, tileList, _difficulty)
            tileList[i] = tile(i, [], minesAround, False)

    return tileList


def boardPrinter(board, _difficulty):
    # this prints out the list that is the current board so it looks like minesweeper
    print("   ", end="")
    for i in range(_difficulty.columns):
        print(base32[i], end=" ")
        # prints out numbers to indicate which column is which
    print("\n")
    for i in range(_difficulty.rows):
        # prints the row idicator and then each tile in that row.
        print(base32[i], end="  ")
        for x in range(_difficulty.columns):
            """the print out still needs to line up so the second case makes
              checked tiles two characters instead of one"""
            if not board[(_difficulty.columns * i) + x].checked:
                print(board[(_difficulty.columns * i) + x].visibleValue, end="")
            if board[(_difficulty.columns * i) + x].checked:
                print(board[(_difficulty.columns * i) + x].visibleValue, end=" ")
        print()


def sweeper(row, column, board, _difficulty):
    """This function is the thing that happens when you check
    an empty tile that is surrounded by other empty tiles.
    it is intended to all of the surrounding empty tiles up
    to the edge of non-empty tiles."""
    spot = board[row * _difficulty.columns + column]
    # ^ current location
    hdict = edgeDict(_difficulty)
    """It works by taking the current tile and checking
    up, then left, then down, then right. if it finds another zero tile it 
    runs itself again on the spot that was a zero tile. if it finds a digit, 
    it checks the two adjacent (up and down, or left and right). if it finds a digit,
    it checks that tile, if it finds another zero, it runs itself again."""
    # Im not sure why the try/except statements are needed, but without them, it doesnt work
    if spot.number not in hdict["top"]:
        up = board[(row - 1) * _difficulty.columns + column]
        # ^ tile location direltcly above spot
        try:
            if up.value == 0 and up.checked == False:
                up.check()
                sweeper(row - 1, column, board, _difficulty)
            elif up.value in digits:
                up.check()
                if spot.number not in hdict["right"]:
                    if board[(row - 1) * _difficulty.columns + column + 1].value == 0 and board[(row - 1) * _difficulty.columns + column + 1].checked == False:
                        # the board location is the top right adjacent tile to spot.
                        sweeper(row - 1, column + 1, board, _difficulty)
                    elif board[(row - 1) * _difficulty.columns + column + 1].value in digits:
                        board[(row - 1) * _difficulty.columns + column + 1].check()
                if spot.number not in hdict["left"]:
                    if board[(row - 1) * _difficulty.columns + column - 1].value == 0 and board[(row - 1) * _difficulty.columns + column - 1].checked == False:
                        # the board location is the top left adjacent tile to spot.
                        sweeper(row - 1, column - 1, board, _difficulty)
                    elif board[(row - 1) * _difficulty.columns + column - 1].value in digits:
                        board[(row - 1) * _difficulty.columns + column - 1].check()
        except IndexError:
            pass
    if spot.number not in hdict["left"]:
        left = board[row * _difficulty.columns + column - 1]
        # ^ tile location directly to the left of spot
        try:
            if left.value == 0 and left.checked == False:
                left.check()
                sweeper(row, column - 1, board, _difficulty)
            elif left.value in digits:
                left.check()
                if spot.number not in hdict["top"]:
                    if board[(row - 1) * _difficulty.columns + column - 1].value == 0 and board[(row - 1) * _difficulty.columns + column - 1].checked == False:
                        # the board location is the top right adjacent tile to spot.
                        sweeper(row - 1, column - 1, board, _difficulty)
                    elif board[(row - 1) * _difficulty.columns + column - 1].value in digits:
                        board[(row - 1) * _difficulty.columns + column - 1].check()
                if spot.number not in hdict["bottom"]:
                    if board[(row + 1) * _difficulty.columns + column - 1].value == 0 and board[(row + 1) * _difficulty.columns + column - 1].checked == False:
                        # the board location is the bottom right adjacent tile to spot.
                        sweeper(row + 1, column - 1, board, _difficulty)
                    elif board[(row + 1) * _difficulty.columns + column - 1].value in digits:
                        board[(row + 1) * _difficulty.columns + column - 1].check()
        except IndexError:
            pass
    if spot.number not in hdict["bottom"]:
        down = board[(row + 1) * _difficulty.columns + column]
        # ^ tile location directly below spot
        try:
            if down.value == 0 and down.checked == False:
                down.check()
                sweeper(row + 1, column, board, _difficulty)
            elif down.value in digits:
                down.check()
                if spot.number not in hdict["right"]:
                    if board[(row + 1) * _difficulty.columns + column + 1].value == 0 and board[(row + 1) * _difficulty.columns + column + 1].checked == False:
                        # the board location is the bottom right adjacent tile to spot.
                        sweeper(row + 1, column + 1, board, _difficulty)
                    elif board[(row + 1) * _difficulty.columns + column + 1].value in digits:
                        board[(row + 1) * _difficulty.columns + column + 1].check()
                if spot.number not in hdict["left"]:
                    if board[(row + 1) * _difficulty.columns + column - 1].value == 0 and board[(row + 1) * _difficulty.columns + column - 1].checked == False:
                        # the board location is the bottom left adjacent tile to spot.
                        sweeper(row + 1, column + 1, board, _difficulty)
                    elif board[(row + 1) * _difficulty.columns + column - 1].value in digits:
                        board[(row + 1) * _difficulty.columns + column - 1].check()
        except IndexError:
            pass
    if spot.number not in hdict["right"]:
        right = board[row * _difficulty.columns + column + 1]
        # ^ Tile location directly to the right of spot
        try:
            if right.value == 0 and not right.checked:
                right.check()
                sweeper(row, column + 1, board, _difficulty)
            elif right.value in digits:
                right.check()
                if spot.number not in hdict["top"]:
                    if board[(row - 1) * _difficulty.columns + column + 1].value == 0 and board[(row - 1) * _difficulty.columns + column + 1].checked == False:
                        # the board location is the top right adjacent tile to spot.
                        sweeper(row - 1, column + 1, board, _difficulty)
                    elif board[(row - 1) * _difficulty.columns + column + 1].value in digits:
                        board[(row - 1) * _difficulty.columns + column + 1].check()
                if spot.number not in hdict["bottom"]:
                    if board[(row + 1) * _difficulty.columns + column + 1].value == 0 and board[(row + 1) * _difficulty.columns + column + 1].checked == False:
                        # the board location is the bottom right adjacent tile to spot.
                        sweeper(row + 1, column + 1, board, _difficulty)
                    elif board[(row + 1) * _difficulty.columns + column + 1].value in digits:
                        board[(row + 1) * _difficulty.columns + column + 1].check()
        except IndexError:
            pass


def countAround(row, column, board, _difficulty, action):
    location = int(column * _difficulty.rows + row)
    currentTile = board[row * _difficulty.columns + column]
    # ^ current location
    edgeCase = edgeDict(_difficulty)
    if location not in edgeCase["left"]:
        if board[location - 1].value in digits:
            if action == "f":
                board[location - 1].countDownValue -= 1
            elif action == "u":
                board[location - 1].countDownValue += 1
    if location not in edgeCase["right"]:
        if board[location + 1].value in digits:
            if action == "f":
                board[location + 1].countDownValue -= 1
            elif action == "u":
                board[location + 1].countDownValue += 1
    if location not in edgeCase["left"] and location not in edgeCase["bottom"]:
        if board[location + _difficulty.columns - 1].value in digits:
            if action == "f":
                board[location + _difficulty.columns - 1].countDownValue -= 1
            elif action == "u":
                board[location + _difficulty.columns - 1].countDownValue += 1
    if location not in edgeCase["bottom"]:
        if board[location + _difficulty.columns].value in digits:
            if action == "f":
                board[location + _difficulty.columns].countDownValue -= 1
            elif action == "u":
                board[location + _difficulty.columns].countDownValue += 1
    if location not in edgeCase["right"] and location not in edgeCase["bottom"]:
        if board[location + _difficulty.columns + 1].value in digits:
            if action == "f":
                board[location + _difficulty.columns + 1].countDownValue -= 1
            elif action == "u":
                board[location + _difficulty.columns + 1].countDownValue += 1
    if location not in edgeCase["top"]:
        if board[location - _difficulty.columns].value in digits:
            if action == "f":
                board[location - _difficulty.columns].countDownValue -= 1
            elif action == "u":
                board[location - _difficulty.columns].countDownValue += 1
    if location not in edgeCase["top"] and location not in edgeCase["left"]:
        if board[location - _difficulty.columns - 1].value in digits:
            if action == "f":
                board[location - _difficulty.columns - 1].countDownValue -= 1
            elif action == "u":
                board[location - _difficulty.columns - 1].countDownValue += 1
    if location not in edgeCase["top"] and location not in edgeCase["right"]:
        if board[location - _difficulty.columns + 1].value in digits:
            if action == "f":
                board[location - _difficulty.columns + 1].countDownValue -= 1
            elif action == "u":
                board[location - _difficulty.columns + 1].countDownValue += 1


def checkAround(row, column, board, _difficulty):
    testValue = False
    location = int(column * _difficulty.rows + row)
    # ^ current location
    edgeCase = edgeDict(_difficulty)
    if location not in edgeCase["left"]:
        board[location - 1].check()
    if location not in edgeCase["right"]:
        board[location + 1].check()
    if location not in edgeCase["left"] and location not in edgeCase["bottom"]:
        board[location + _difficulty.columns - 1].check()
    if location not in edgeCase["bottom"]:
        board[location + _difficulty.columns].check()
    if location not in edgeCase["right"] and location not in edgeCase["bottom"]:
        board[location + _difficulty.columns + 1].check()
    if location not in edgeCase["top"]:
        board[location - _difficulty.columns].check()
    if location not in edgeCase["top"] and location not in edgeCase["left"]:
        board[location - _difficulty.columns - 1].check()
    if location not in edgeCase["top"] and location not in edgeCase["right"]:
        board[location - _difficulty.columns + 1].check()


def youDied():
    shrapnel = str(random.randint(5, 250))
    for i in playBoard:
        if i.value == "M" and i.visibleValue != "F ":
            i.visibleValue = "M "
        if i.visibleValue == "F " and i.value != "M":
            i.visibleValue = "X "
    boardPrinter(playBoard, level)
    print("\n")
    print("You clicked on a mine! %s shrapnel pieces are now lodged in your body." % shrapnel, end="\n\n")
    print("although you are still living at the moment, it is in the best interest for all parties involved for you to be declared officially deceased.", end="\n\n")
    print("your family will be notified within the next 8-10 business days", end="\n\n")
    while True:
        newGame = str.lower(input("Would you like to play again? Y/N\n\n"))
        if newGame == "y":
            print("\033[H\033[J")
            print("\n")
            break
            # Restarts the loop from line 275
        elif newGame == "n":
            exit()
        else:
            print("one of your inputs did not match, please try again\n\n")


# from here and down is the actual playing part

while True:
    acceptableActions = ["c", "f", "u"]
    difficultyInput = str.lower(input("Enter difficulty: Easy, Medium, or Hard \n"))
    acceptableDifficulties = {"easy": difficulty(9, 9, 10),
                              "medium": difficulty(16, 16, 40),
                              "hard": difficulty(16, 30, 99)
                              }
    while True:
        if difficultyInput not in acceptableDifficulties:
            difficultyInput = str.lower(
                input("your entered difficulty did not match. Please type 'Easy', 'Medium', or 'Hard'"))
        else:
            break
    level = acceptableDifficulties[difficultyInput]
    playBoard = boardMaker(level)
    print("\033[H\033[J")
    boardPrinter(playBoard, level)
    winCondition = 0
    print("\n acceptable actions include typing 'c' for click tiles, 'f' to flag tiles, and 'u' to unflag tiles \n")
    while True:
        while True:
            # All of this while loop makes sure your input is valid
            choice = input("type row, column and action in this format: 'row, column, action'\n\n")
            print()
            qz = choice.replace(",", "")
            b = qz.replace(" ", "")
            inputs = list(b)
            if len(inputs) == 3 and str(inputs[0]) in base32[0:level.rows] and str(inputs[1]) in base32[
                                                                                                 0:level.columns]:
                rowChoice = base32.index(inputs[0])
                columnChoice = base32.index(inputs[1])
            else:
                print("\033[H\033[J")
                boardPrinter(playBoard, level)
                print("\none of your inputs did not match,please try again\n")
                continue
            tileChoice = playBoard[rowChoice * level.columns + columnChoice]
            action = inputs[2]
            if action in acceptableActions and rowChoice < level.rows and columnChoice < level.columns:
                break
            print("\033[H\033[J")
            boardPrinter(playBoard, level)
            print("\none of your inputs did not match, please try again\n")
        if action == "c":
            # checks the clicked tile
            if tileChoice.value == 0:
                sweeper(rowChoice, columnChoice, playBoard, level)
            elif tileChoice.checked == True and tileChoice.value in digits:
                checkAround(rowChoice, columnChoice, playBoard, level)
            elif tileChoice.visibleValue == "F ":
                print("you may not click a flagged tile. please unflag it first\n")
                continue
            elif tileChoice.value == "M":
                youDied()
                break
            else:
                tileChoice.check()
        if action == "f":
            # flags selected tile
            if level.flags < 0:
                print("you have run out of flags\n\n")
                continue
            elif not tileChoice.checked:
                tileChoice.visibleValue = "F "
                level.flags -= 1
                if tileChoice.value == "M":
                    winCondition += 1
            else:
                print("You may not flag an already checked tile, please try again\n")
                continue
            countAround(rowChoice, columnChoice, playBoard, level, action)
        if action == "u":
            # un-flags selected tile
            if tileChoice.visibleValue == "F ":
                tileChoice.visibleValue = []
                level.flags += 1
            else:
                print("you may not unflag a tile that has not already been flagged\n")
            countAround(rowChoice, columnChoice, playBoard, level, action)
        if winCondition == level.mines:
            for i in range(0, random.randint(76, 400)):
                if i % 7 == 0:
                    print("roncgatlutaniot! v'eoyu nwo¡")
                elif i % 23 == 0:
                    print("¡uoʍ ǝʌ,noʎ ¡suoᴉʇɐlnʇɐɹƃuoɔ")
                else:
                    print("congratulations! you've won!")
                time.sleep(.03)
            print()
            for i in playBoard:
                if i.value != "M":
                    i.check()
            boardPrinter(playBoard, level)
            while True:
                newGame = str.lower(input("Would you like to play again? Y/N"))
                if newGame == "y":
                    print("\033[H\033[J")
                    print()
                    break
                    # restarts the entire playing loop
                elif newGame == "n":
                    exit()
                else:
                    print("one of your inputs did not match, please try again")
            break
        print("\033[H\033[J")
        boardPrinter(playBoard, level)

        print("\n\nYou have %d flags left" % level.flags)
        # prints the board after all actions have been made
        print()
