"""
Ths is our main Driver file. It will:
 - process user input
 - display current GameState object
"""

import pygame as p
from Chess import ChessEngine
import os

p.init()  # may be useless
WIDTH = HEIGHT = 512  # 400 works too
DIMENSION = 8  # 8x8
SQ_SIZE = WIDTH//DIMENSION
MAX_FPS = 15  # for animation later
IMAGES = {}

'''
Only load images once, it's an expensive task:
Initialize global dictionary of images. 
'''

def load_images():
    directory = '/Users/roman/Python Shiz/unpack later/Personal Mess/Chess/Chess/images'
    for image in os.listdir(directory):
        if not image.startswith('.DS_Store'):
            IMAGES[image] = p.transform.scale(p.image.load("images/" + image), (SQ_SIZE, SQ_SIZE))
    # we can now use images using IMAGES[image]

'''
This will be our main driver and handle user input and update graphics
'''
def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("green"))  # fill screen with background colour, can delete later on

    gs = ChessEngine.GameState()  # this will initialise the constructor and creates (board, ToMove and log) variables
    valid_moves = gs.get_valid_moves()
    move_made = False # flag variable for hwen move is made, so we don't calculate all next moves every time

    load_images()  # only do this once, before the while loop
    running = True
    sq_selected = ()  # don't want to keep track of row and column, allows global usage of coords. Tracks last click
    player_clicks = []  # tracks clicks, has two tuples [(), ()]

    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            # mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()  # (x, y) coordinates of mouse. if add extra stuff, 5:01 of vid 1
                col = location[0]//SQ_SIZE
                row = location[1]//SQ_SIZE  # these need to be integers --> //
                print(col, row)
                if sq_selected == (row, col):  # user clicked same square twice
                    sq_selected = ()  # undo
                    player_clicks = []  # clears player clicks
                else:
                    sq_selected = (row, col)
                    player_clicks.append(sq_selected)  # append for both 1st and 2nd clicks
                if len(player_clicks) == 2:
                    move = ChessEngine.Move(player_clicks[0], player_clicks[1], gs.board)
                    print(move.get_chess_notation())
                    # we need to log if the move is en-passant or pawn promotion
                    for i in range(len(valid_moves)):
                        if move == valid_moves[i]:
                            gs.make_move(valid_moves[i])  # having this instead of (move) argument means ENGINE is making the move
                            move_made = True
                            sq_selected = ()  # reset user inputs
                            player_clicks = []
                    if not move_made:  # invalid move
                        player_clicks = [sq_selected]  # avoids double clicking issue
            # key handler
            elif e.type ==p.KEYDOWN:
                if e.key == p.K_z:  # undo when 'z' is pressed
                    gs.undo_move()
                    move_made = True

        if move_made:
            valid_moves = gs.get_valid_moves()  # generate new valid moves, only when a valid move is made
            move_made = False

        draw_game_state(screen, gs)
        clock.tick(MAX_FPS)
        p.display.flip()
    print(gs.board)

'''
Responsible for all graphics within a current game state
'''


def draw_game_state(screen, gs):
    draw_board(screen)  # draw squares on board
    #  add in piece highlighting or move suggestions (red dot?) later
    draw_pieces(screen, gs.board)  # draw pieces on top of squares


'''
Draw the squares on the board. Top left square is always light 
'''

def draw_board(screen):
    colours = [p.Color("light gray"), p.Color("brown")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            colour = colours[((r + c) % 2)]
            p.draw.rect(screen, colour, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))



'''
Draw the pieces on the board using current GameState.board
'''
def draw_pieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = str(board[r][c]) + '.png'
            if piece != '--.png':  # not empty square
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))


if __name__ == '__main__':
    main()



