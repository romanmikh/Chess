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



def load_images():
    '''
    Only load images once, it's an expensive task.
    Initialize global dictionary of images.
    '''
    directory = '/Users/roman/Python Shiz/GitHub_Reps/Chess/Chess/images'
    for image in os.listdir(directory):
        if not image.startswith('.DS_Store'):
            IMAGES[image] = p.transform.scale(p.image.load("images/" + image), (SQ_SIZE, SQ_SIZE))
    # we can now use images using IMAGES[image]


def main():
    '''
    This will be our main driver and handle user input and update graphics
    '''
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    screen.fill(p.Color("green"))  # fill screen with background l, can delete later on

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
            animation(gs.moveLog[-1], screen, gs.board, clock)
            valid_moves = gs.get_valid_moves()  # generate new valid moves, only when a valid move is made
            move_made = False

        draw_game_state(screen, gs, valid_moves, sq_selected)
        clock.tick(MAX_FPS)
        p.display.flip()
    print(gs.board)





def highlight(screen, gs, valid_moves, sq_selected):
    '''
    Highlight selected square and possible move squres
    '''
    if sq_selected != ():
        r, c = sq_selected
        if gs.board[r][c][0] == ('w' if gs.white_to_move else 'b'): # nested. Making sure that selected square can be moved
            s = p.Surface((SQ_SIZE, SQ_SIZE))  # double brackets since surface takes (x, y) coordinates
            s.set_alpha(100) # 0 is transparent, 255 is opaque
            s.fill(p.Color('green'))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            # highlighting poss destination squares
            s.fill(p.Color('blue'))
            for move in valid_moves:
                if move.start_row == r and move.start_col == c:
                    screen.blit(s, (move.end_col * SQ_SIZE, move.end_row * SQ_SIZE))  # input format is (y, x)



def draw_game_state(screen, gs, valid_moves, sq_selected):
    '''
    Responsible for all graphics within a current game state
    '''
    draw_board(screen)  # draw squares on board
    highlight(screen, gs, valid_moves, sq_selected)
    #  add in piece highlighting or move suggestions (red dot?) later
    draw_pieces(screen, gs.board)  # draw pieces on top of squares




def draw_board(screen):
    '''
    Draw the squares on the board. Top left square is always light
    '''
    global colors
    colors = [p.Color("light gray"), p.Color("brown")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))




def draw_pieces(screen, board):
    '''
    Draw the pieces on the board using current GameState.board
    '''
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = str(board[r][c]) + '.png'
            if piece != '--.png':  # not empty square
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))



def animation(move, screen, board, clock):
    '''
    Animate piece movement. It'd be more efficient to redraw only the relevant section. But the move animations are
    low rendering and don't occur for a lot of the time the code runs, this is ok.
    '''
    global colors
    d_row = move.end_row - move.start_row
    d_col = move.end_col - move.start_col
    frames_per_square = 10
    frame_count = (abs(d_row) + abs(d_col)) * frames_per_square
    for frame in range(frame_count + 1):  # +1 to take us to the end of the move
        # (r, c), deciding fractional change in separate frames
        r, c = (move.start_row + d_row*frame/frame_count, move.start_col + d_col*frame/frame_count)
        draw_board(screen)
        draw_pieces(screen, board)
        # erase the piece immediately moved to its ending square por defecto
        color = colors[(move.end_row + move.end_col)%2]
        end_square = p.Rect(move.end_col*SQ_SIZE, move.end_row*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, end_square)
        # draw captured piece onto rectangle
        if move.piece_captured != '--':
            screen.blit(IMAGES[move.piece_captured], end_square)
        # draw moving piece
        screen.blit(IMAGES[move.piece_moved], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))  # TODO add .png format
        # puts it at its location at whatever frame of the animation
        p.display.flip()
        clock.tick(80)


if __name__ == '__main__':
    main()



