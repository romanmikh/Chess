"""
Ths is the main compiling file. It:
 - processes user input
 - displays current GameState object
"""

import pygame as p
from Chess import Chess_Logic

WIDTH = HEIGHT = 600  # 512 & 400 scale nicely with the icons
BOARD_LENGTH = 8  # 8x8
SQ_LENGTH = WIDTH // BOARD_LENGTH
MAX_FPS = 60
ICONS = {}


def load_icons():
    '''
    Only load icons once - it's an expensive task. Initialise global dictionary of images
    '''
    icons = ['wK', 'wQ', 'wR', 'wB', 'wN', 'wP', 'bK', 'bQ', 'bR', 'bB', 'bN', 'bP']
    for icon in icons:
        ICONS[icon] = p.transform.scale(p.image.load("Chess_Icons/" + icon + '.png'), (SQ_LENGTH, SQ_LENGTH))
    # we can now use icons with ICONS[icon]


def main():
    '''
    Handle user input and update graphics
    '''
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    clock = p.time.Clock()
    # screen.fill(p.Color("green"))  # fill screen with background l, can delete later on TODO

    gs = Chess_Logic.GameState()  # this will initialise the constructor and creates (board, ToMove and log) variables
    valid_moves = gs.get_valid_moves()
    player_clicks = []  # tracks clicks, takes two tuples [(), ()]
    sq_selected = ()  # tracks last click. TODO don't want to keep track of row and column, allows global usage of coords.
    load_icons()  # only do this once, before the while loop
    move_made = False  # flag variable for when move is made, so we don't calculate all next moves every time
    animate = False  # flag variable for when we should animate move, can make animation optional altogether with this
    running = True  # flag variable necessary for closing the window
    game_over = False

    while running:
        for e in p.event.get():
            if e.type == p.QUIT:  # clicking 'x'
                running = False

            # mouse handler
            if e.type == p.MOUSEBUTTONDOWN:
                if not game_over:
                    location = p.mouse.get_pos()  # (x, y) coordinates of mouse. if add extra stuff, 5:01 of vid 1
                    col = location[0] // SQ_LENGTH
                    row = location[1] // SQ_LENGTH  # row & col need to be integers --> '//'
                    # print(col, row)
                    if sq_selected == (row, col):  # user clicked on same square twice
                        sq_selected = ()  # undo
                        player_clicks = []  # clears player clicks
                    else:
                        sq_selected = (row, col)
                        player_clicks.append(sq_selected)  # append for both 1st and 2nd clicks
                    if len(player_clicks) == 2:
                        move = Chess_Logic.Move(player_clicks[0], player_clicks[1], gs.board)
                        print(move.get_chess_notation())

                        # we need to log if the move is en-passant or pawn promotion
                        for i in range(len(valid_moves)):
                            if move == valid_moves[i]:
                                gs.make_move(valid_moves[i])  # TODO having this instead of (move) argument means LOGIC is making the move
                                move_made = True
                                animate = True
                                sq_selected = ()  # reset user inputs
                                player_clicks = []
                        if not move_made:  # invalid move
                            player_clicks = [sq_selected]  # fixes the double clicking issue
            # key handler
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:  # undo move when 'z' is pressed
                    gs.undo_move()
                    move_made = True
                    animate = False
                if e.key == p.K_r:  # resets board when 'r' is pressed
                    gs = Chess_Logic.GameState()  # necessary to reset GameState
                    valid_moves = gs.get_valid_moves()
                    sq_selected = ()
                    player_clicks = []
                    move_made = False
                    animate = False

        if move_made:
            if animate:
                animation(gs.moveLog[-1], screen, gs.board, clock)
            valid_moves = gs.get_valid_moves()  # generate new valid moves, only when a valid move is made
            move_made = False
            animate = False

        draw_game_state(screen, gs, valid_moves, sq_selected)
        # after w draw our GameState we check if game is over
        if gs.checkmate:
            game_over = True
            if gs.white_to_move:
                draw_text(screen, 'Black wins by checkmate')  # if game ends on white's turn
            else:
                draw_text(screen, 'White wins by checkmate')  # vice versa

        if gs.stalemate:
            game_over = True
            if gs.white_to_move:
                draw_text(screen, 'Black wins by stalemate')
            else:
                draw_text(screen, 'White wins by stalemate')

        clock.tick(MAX_FPS)
        p.display.flip()
    print(gs.board)


def draw_game_state(screen, gs, valid_moves, sq_selected):
    '''
    Responsible for all graphics within a current game state
    '''
    draw_board(screen)  # draw squares on board
    highlight(screen, gs, valid_moves, sq_selected)  # draw highlights
    plot_pieces(screen, gs.board)  # draw pieces on top of squares


def draw_board(screen):
    '''
    Draw the squares on the board. Top left square is always light
    '''
    global colours
    colours = [p.Color("white"), p.Color("brown")]
    for r in range(BOARD_LENGTH):
        for c in range(BOARD_LENGTH):
            colour = colours[((r + c) % 2)]  # neat trick. Scans through 2D array, odd/even squares are coloured
            p.draw.rect(screen, colour, p.Rect(c * SQ_LENGTH, r * SQ_LENGTH, SQ_LENGTH, SQ_LENGTH))


def highlight(screen, gs, valid_moves, sq_selected):
    '''
    Highlight selected square and all possible destination squares
    '''
    if sq_selected != ():
        r, c = sq_selected
        if gs.board[r][c][0] == ('w' if gs.white_to_move else 'b'):  # nested 'if' statement. Appropriating player turns
            s = p.Surface((SQ_LENGTH, SQ_LENGTH))  # double brackets since surface takes (x, y) coordinates
            s.set_alpha(100)  # 0 is transparent, 255 is opaque
            s.fill(p.Color('green'))
            screen.blit(s, (c * SQ_LENGTH, r * SQ_LENGTH))
            # highlighting poss destination squares
            s.fill(p.Color('blue'))
            for move in valid_moves:
                if move.start_row == r and move.start_col == c:
                    screen.blit(s, (move.end_col * SQ_LENGTH, move.end_row * SQ_LENGTH))  # input format is (y, x)


def plot_pieces(screen, board):
    '''
    Draw the pieces on the board using current GameState.board
    '''
    for r in range(BOARD_LENGTH):
        for c in range(BOARD_LENGTH):
            piece = str(board[r][c])
            if piece != '--':  # not clicked on empty square
                screen.blit(ICONS[piece], p.Rect(c * SQ_LENGTH, r * SQ_LENGTH, SQ_LENGTH, SQ_LENGTH))


def animation(move, screen, board, clock):
    '''
    Animate piece movement. It'd be more efficient to redraw only the relevant section. But the move animations are
    low rendering and don't occupy much code runtime, this is ok.
    '''
    global colours
    d_row = move.end_row - move.start_row
    d_col = move.end_col - move.start_col
    frames_per_square = 5
    frame_count = (abs(d_row) + abs(d_col)) * frames_per_square
    for frame in range(frame_count + 1):  # +1 ensures piece moves all the way
        # (r, c), deciding fractional change in separate frames
        r, c = (move.start_row + d_row * frame / frame_count, move.start_col + d_col * frame / frame_count)
        draw_board(screen)
        plot_pieces(screen, board)
        # erase the piece immediately moved to its ending square/colour square in again
        color = colours[(move.end_row + move.end_col) % 2]
        end_square = p.Rect(move.end_col * SQ_LENGTH, move.end_row * SQ_LENGTH, SQ_LENGTH, SQ_LENGTH)
        p.draw.rect(screen, color, end_square)
        # draw captured piece onto rectangle
        if move.piece_captured != '--':
            screen.blit(ICONS[move.piece_captured], end_square)
        # draw moving piece
        screen.blit(ICONS[move.piece_moved], p.Rect(c * SQ_LENGTH, r * SQ_LENGTH, SQ_LENGTH, SQ_LENGTH))
        # puts it at its location at whatever frame of the animation
        p.display.flip()
        clock.tick(400)


def draw_text(screen, text):
    font = p.font.SysFont("Times New Roman", 40, True, False)
    text_object = font.render(text, 0, p.Color('Green'))
    text_location = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH / 2 - text_object.get_width() / 2,
                                                     HEIGHT / 2 - text_object.get_height() / 2)  # centering text
    screen.blit(text_object, text_location)
    text_object = font.render(text, 0, p.Color('Blue'))
    screen.blit(text_object, text_location.move(2, 2))


if __name__ == '__main__':
    main()



