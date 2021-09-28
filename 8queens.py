from connectfour import DoneButton
import cv2
from time import sleep

from numpy.lib.shape_base import row_stack
import HandTrackingModule as htm
import time
import random
import numpy as np
from datetime import datetime


init_time = time.time()
timer_timeout_text = init_time+1
timer_timeout = init_time+1
counter_timeout = init_time+1
counter_timeout_text = init_time+1


def draw_text(frame, text, x, y, color=(255,0,255), thickness=4, size=3):
    if x is not None and y is not None:
        cv2.putText(frame, text, (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, size, color, thickness)


def drawAll(img, buttonList = [], button1 = None, button2 = None):
    for button in buttonList:
        x, y = button.pos
        w, h = button.size
        cv2.rectangle(img, button.pos, (x + w, y + h), (255, 0, 0), cv2.FILLED)
    if button1:
        x1, y1 = button1.pos
        w1, h1 = button1.size
        cv2.rectangle(img, button1.pos, (x1 + w1, y1 + h1), (175, 0, 175), cv2.FILLED)
        cv2.putText(img, button1.text, (x1 + 50, y1 + 70),cv2.FONT_HERSHEY_PLAIN, 4, (0, 0, 128), 4)
    if button2:
        x1, y1 = button2.pos
        w1, h1 = button2.size
        cv2.rectangle(img, button2.pos, (x1 + w1, y1 + h1), (175, 0, 175), cv2.FILLED)
        cv2.putText(img, button2.text, (x1 + 50, y1 + 70),cv2.FONT_HERSHEY_PLAIN, 4, (0, 0, 128), 4)
    return img
        
def draw(img,id):
    button = buttonList[id]
    x, y = button.pos
    w, h = button.size
    cv2.rectangle(img, button.pos, (x + w, y + h), (0, 255, 255), cv2.FILLED)
    return img

class Button():
    def __init__(self, pos, row,column,size=[192, 190]):
        self.pos = pos
        self.size = size
        self.row = row
        self.column = column

class DoneButton():
    def __init__(self, pos, text, size=[230, 230]):
        self.pos = pos
        self.size = size
        self.text = text

buttonList = []
for i in range(6):
    for j in range(6):
        if (i == 0 and j == 0):
            buttonList.append(Button([300 * j + 400, 50 * i + 50], str(i), str(j)))
        elif j>=0 and i != 0:
            buttonList.append(Button([300 * j + 400, 250 * i + 50], str(i), str(j)))
        else:
            buttonList.append(Button([300 * j + 400, 250 * i + 50], str(i), str(j)))
doneButton = DoneButton([2500, 900], "Change", size = [400, 100])
playButton = DoneButton([2500, 720], "Play", size = [400, 100])
ROW_COUNT = 6
COLUMN_COUNT = 6

def create_board():
	board = np.zeros((ROW_COUNT,COLUMN_COUNT))
	return board

def drop_piece(board, row, col, piece):
	board[row][col] = piece

def check_attack(row, col, board):
    # Check if this queen attacks other queens in the candidate
    for q_col in range(COLUMN_COUNT):
        if q_col == col:
            continue
        else:
            if board[row][q_col] == 1:
                return True
    for q_row in range(ROW_COUNT):
        if q_row == row:
            continue
        else:
            if board[q_row][col] == 1:
                return True

    for q_row in range(ROW_COUNT):
        for q_col in range(COLUMN_COUNT):
            if q_col == col and q_row == row:
                # skip if its the same queen we are checking
                continue
            else:
                if abs(row - q_row) == abs(col - q_col):
                    if board[q_row][q_col] == 1:
                        return True
    else:
        return False

def check_win(board):
    for q_row in range(ROW_COUNT):
        if list(board[q_row]).count(1) != 1:
            return False

    else:
        return True

image = cv2.imread('queen.png')

cap = cv2.VideoCapture(0)
show = True
invalid = False
detector = htm.handDetector(detectionCon=0.8)
done = False
board = create_board()
gameOver = False
timer = 5


st = -1.0
et = -1.0
time_taken = 0
coorx = 0
coory = 0
while True:
    success, img = cap.read()
    
    img = cv2.resize(img,(3000,1900),fx=0,fy=0, interpolation = cv2.INTER_CUBIC)


    
    img = cv2.flip(img, 1)
    center_x = int(img.shape[0]/2)
    center_y = int(img.shape[0]/2)
    
    
    _, img = detector.findHands(img)
    
    lmList, bboxInfo = detector.findPosition(img)


    img = drawAll(img, buttonList, doneButton, playButton)
    
    if time.time() > timer_timeout_text and timer >0:
        wait2 = 10000
        while wait2 > 0:
            draw_text(img, "Timer: "+str(timer), center_x+1300, center_y-700, (0,255,255), 10, 5)
            wait2 -= 1
        timer_timeout_text+=0.03333
    else:
        # time.sleep(1)
        # sc = sc+1
        # if sc > 9 and sc <60:
        #     sec = sc
        # elif sc <= 9:
        #     sec = "0"+str(sc)
        # if sc == 60:
        #     mn += 1
        #     if mn > 9 and mn <60:
        #         min = mn
        #     elif mn <= 9:
        #         min = "0"+str(mn)+":"
        #     sc = 0
        # if mn == 60:
        #     hr += 1
        #     mn = 0
        if timer <= 0 and show == True:
            draw_text(img, str(time.strftime('%H:%M:%S')), center_x+1300, center_y-500,color = (0,255,255), thickness = 10, size = 3)
        # if time.time() > counter_timeout_text and counter >0:
        #     draw_text(img, "Counter: "+str(counter), center_x+1300, center_y-700, (0,255,255), 8, 5)
        #     timer_timeout_text+=0.03333
        if lmList:
            if not done and not gameOver:
                for button in buttonList:
                    x, y = button.pos
                    w, h = button.size

                    if x < lmList[8][1] < x + w and y < lmList[8][2] < y + h: 

                        cv2.rectangle(img, (x - 5, y - 5), (x + w + 5, y + h + 5), (250, 206, 135), cv2.FILLED)
                        l, _, _ = detector.findDistance(8, 12, img)

                        if l < 100:
                            cv2.rectangle(img, button.pos, (x + w, y + h), (0, 255, 0), cv2.FILLED)
                            if not check_attack(int(button.row), int(button.column), board):
                                #queens.append(button)
                                board[int(button.row)][int(button.column)] = 1
                                sleep(0.15)
                                #print(board)
                                break
                            elif check_attack(int(button.row), int(button.column), board):
                                x2, y2 = button.pos
                                w2, h2 = button.size
                                cv2.rectangle(img, button.pos, (x2 + w2, y2 + h2), (0, 0, 255), cv2.FILLED)
                                invalid = True
            
                x1, y1 = doneButton.pos
                w1, h1 = doneButton.size
                if x1 < lmList[8][1] < x1 + w1 and y1 < lmList[8][2] < y1 + h1:

                    cv2.rectangle(img, (x1 - 5, y1 - 5), (x1 + w1 + 5, y1 + h1 + 5), (193, 182, 255), cv2.FILLED)
                    l, _, _ = detector.findDistance(8, 12, img)
                    
                    
                    if l < 100:
                        cv2.rectangle(img, doneButton.pos, (x1 + w1, y1 + h1), (0, 255, 0), cv2.FILLED)
                        
                        done = True

            if done == True:
                for button in buttonList:
                    x, y = button.pos
                    w, h = button.size

                    if x < lmList[8][1] < x + w and y < lmList[8][2] < y + h: 

                        cv2.rectangle(img, (x - 5, y - 5), (x + w + 5, y + h + 5), (250, 206, 135), cv2.FILLED)
                        l, _, _ = detector.findDistance(8, 12, img)

                        if l < 100:
                            cv2.rectangle(img, button.pos, (x + w, y + h), (0, 255, 0), cv2.FILLED)
                            board[int(button.row)][int(button.column)] = 0
                            break

                    
            x1, y1 = playButton.pos
            w1, h1 = playButton.size
            if x1 < lmList[8][1] < x1 + w1 and y1 < lmList[8][2] < y1 + h1:

                cv2.rectangle(img, (x1 - 5, y1 - 5), (x1 + w1 + 5, y1 + h1 + 5), (193, 182, 255), cv2.FILLED)
                l, _, _ = detector.findDistance(8, 12, img)
                
                
                if l < 100:
                    cv2.rectangle(img, playButton.pos, (x1 + w1, y1 + h1), (0, 255, 0), cv2.FILLED)
                    
                    done = False
            

                
        


        # for queen in queens:
        #     if coorx == queen.row and coory == queen.column:
        #         print(queen.row, queen.column)
        #     x, y = queen.pos
        #     w, h = queen.size
        #     drop_piece(board, int(queen.row), int(queen.column), 1)
        #     x1,y1 = x+w//2, y+h//2
        #     draw_text(img, "Q", x1, y1, color=(255,255,255), thickness=10, size=3)
        for button in buttonList:
            for rows in range(ROW_COUNT):
                for columns in range(COLUMN_COUNT):
                    if board[rows][columns] == 1 and rows == int(button.row) and columns == int(button.column):
                        x, y = button.pos
                        w, h = button.size
                        x1,y1 = x+w//2, y+h//2
                        draw_text(img, "Q", x1-5, y1-5, color=(0,255,255), thickness=10, size=3)
                        img[button.pos[1]:button.pos[1]+image.shape[0], button.pos[0]:button.pos[0]+image.shape[1]] = image


        if check_win(board):
            gameOver = True
            show = False


        if gameOver:
            et = time.strftime('%H:%M:%S')
            FMT = '%H:%M:%S'
            if type(et) is not int and type(st) is not int:
                time_taken = datetime.strptime(et, FMT) - datetime.strptime(st, FMT)
                print(time_taken)
                st = -1
                et = -1
            

        if invalid:
            draw_text(img, "Attacked!!", center_x+1300, center_y-600,color = (0,255,255), thickness = 10, size = 3)
            invalid = False


        # if time.time() > counter_timeout:
        #     counter+=1
        #     counter_timeout += 1
        

    if time.time() > timer_timeout:
        timer-=1
        timer_timeout += 1
    if timer == 0:
        st = time.strftime('%H:%M:%S')
        draw_text(img, "Start Time: ", center_x+1300, center_y-800, (0,255,255), 10, 3)
        draw_text(img, str(st), center_x+1300, center_y-700, (0,255,255), 10, 3)


    
    
    

    if timer <= 0:
        if time_taken == 0:
            draw_text(img, "".format(time_taken), center_x+1300, center_y-600,color = (0,255,255), thickness = 12, size = 2)
        else:
            draw_text(img, "You took: {}".format(time_taken), center_x+1300, center_y-600,color = (0,255,255), thickness = 12, size = 2)
    cv2.imshow("Image", img)

    
    
    if (cv2.waitKey(1) & 0xFF == ord('q')):
        break

cap.release()
cv2.destroyAllWindows()