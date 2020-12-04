"""
This class is where we will:
 - store all the data about the current state of a chess game
 - determine legal moves of the current state
 - keep a move log (for undo, look back etc.)
"""


class GameState():
    def __init__(self):  # constructor
        # the board is an 8x8 2D list, each element has 2 chars. char1 = colour (b, w), char2 = piece (K,Q,R,N,B,P)
        # '--' represents an empty square with no piece
        self.board = [
            ['bR', 'bN', 'bB', 'bQ', 'bK', 'bB', 'bN', 'bR'],
            ['bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP', 'bP'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['--', '--', '--', '--', '--', '--', '--', '--'],
            ['wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP', 'wP'],
            ['wR', 'wN', 'wB', 'wQ', 'wK', 'wB', 'wN', 'wR']]
        self.move_functions = {'P': self.get_pawn_moves, 'B': self.get_bishop_moves, 'Q': self.get_queen_moves,
                               'R': self.get_rook_moves, 'N': self.get_knight_moves, 'K': self.get_king_moves}
        # don't need parenthesis, params will be passed later

        self.whiteToMove = True
        self.moveLog = []
        self.white_king_loc = (7, 4)
        self.black_king_loc = (0, 4)
        self.in_check = False
        self.pins = []
        self.checks = []
        self.checkmate = False
        self.stalemate = False
        self.en_passant_is_poss = ()  # coords of square that en-passant terminates on (posibly)
        # self.current_castling_right = CastleRights(True, True, True, True)
        # castling rights
        self.white_castle_kingside = True
        self.black_castle_kingside = True
        self.white_castle_queenside = True
        self.black_castle_queenside = True
        # self.castle_rights_log = [CastleRights(self.current_castling_right.wks, self.current_castling_right.bks,
        #                                         self.current_castling_right.wqs, self.current_castling_right.bqs)]
        self.castle_rights_log = [CastleRights(self.current_castling_right, self.current_castling_right,
                                               self.current_castling_right, self.current_castling_right)]
        # now log actually keeps track of changes



    '''
    Takes move as a parameter and updates it (except for castling, en-passant and pawn promotion'''
    def make_move(self, move):
        self.board[move.start_row][move.start_col] = "--"
        self.board[move.end_row][move.end_col] = move.piece_moved
        # we can assume this move is already valid
        self.moveLog.append(move)  # log the move so we can undo it later
        self.whiteToMove = not self.whiteToMove # swap players
        # update kings' locations
        if move.piece_moved == 'wK':
            self.white_king_loc = (move.end_row, move.end_col)
        elif move.piece_moved == 'bK':
            self.black_king_loc = (move.end_row, move.end_col)

        # if pawn moves twice, we can capture en-passant
        # now we need to update self.en_passant_is_poss = () with every move, else code doesn't work
        if move.piece_moved[1] == 'P' and abs(move.start_row - move.end_row) == 2:  # only on 2 move advances
            self.en_passant_is_poss = ((move.start_row + move.end_row)//2, move.end_col)  # // does INTERGER DIVISION, / DOES DECIMAL
        else:
            self.en_passant_is_poss = ()  # reset it if it wasn't an en-passant

        # if pawn moves twice, we can capture en-passant
        if move.enPassant:
            self.board[move.start_row][move.end_col] = '--'  # capturing pawn

        # pawn promotion
        if move.is_pawn_promotion:
            promoted_piece = input('Choose Q, R, B or N:')  # make this part of UI later
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + promoted_piece

        # castle move
        if move.is_castle_move:
            if move.end_col - move.start_col == 2:  # kingside castle
                self.board[move.end_row][move.end_col - 1] = self.board[move.end_row][move.end_col + 1]  # moves the rook
                self.board[move.end_row][move.end_col + 1] = '--'  # delete old rook
            else:  # queenside castle
                self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.endcol - 2]  # moves the rook
                self.board[move.end_row][move.end_col - 2] = '--'  # delete old rook

        # update castling rights whenever king or rook moves
        self.update_castle_rights(move)
        # self.castle_rights_log.append(CastleRights(self.current_castling_right.wks, self.current_castling_right.bks,
        #                                             self.current_castling_right.wqs, self.current_castling_right.bqs))
        self.castle_rights_log = [CastleRights(self.current_castling_right, self.current_castling_right,
                                               self.current_castling_right, self.current_castling_right)]
        # this allows us to undo move



    '''
    Undo the last move
    '''
    def undo_move(self):
        if len(self.moveLog) != 0:  # ensure there's a move to undo
            move = self.moveLog.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved  # put piece on starting square
            self.board[move.end_row][move.end_col] = move.piece_captured  # put back captured piece
            self.whiteToMove = not self.whiteToMove  # swap turns back
            # undo kings' moves + update king's position
            if move.piece_moved == 'wK':
                self.white_king_loc = (move.start_row, move.start_col)
            elif move.piece_moved == 'bK':
                self.black_king_loc = (move.start_row, move.start_col)

            # undo en-passant move
            if move.enPassant:
                self.board[move.end_row][move.end_col] = '--'  # leave landing square blank. Remove pawn that was added to the wrong square
                self.board[move.start_row][move.end_col] = move.piece_captured  # puts pawn back in correct square it was captured from
                self.en_passant_is_poss = (move.end_row, move.end_col)  # crucial - allows enpassant to happen in next move
            # undo 2 square pawn advance
            if move.piece_moved[1] == 'P' and abs(move.start_row - move.end_row) == 2:
                self.en_passant_is_poss = ()

            # undo castle move
            if move.is_castle_move:
                if move.end_col - move.start_col == 2:  # kingside
                    self.board[move.end_row][move.end_col + 1] = self.board[move.end_row][move.end_col - 1]
                    self.board[move.end_row][move.end_col - 1] = '--'
                else:  # queenside
                    self.board[move.end_row][move.end_col - 2] = self.board[move.end_row][move.end_col + 1]
                    self.board[move.end_row][move.end_col + 1] = '--'

            # undo castling
            self.castle_rights_log.pop()  # delete last element, get rid of castle rights from move we are undoing
            self.current_castling_right = self.castle_rights_log[-1]  # et current castle rights to last one on list
            self.white_castle_kingside = current_castling_right.wks
            self.black_castle_kingside = current_castling_right.bks
            self.white_castle_queenside = current_castling_right.wqs
            self.black_castle_queenside = current_castling_right.bqs









    '''
    All moves without considering checks ( possible moves )
    '''
    def get_poss_moves(self):
        moves = []
        for r in range(len(self.board)):  # go through board by row and column
            for c in range(len(self.board[r])):  # this is proper nested loops notation
                turn = self.board[r][c][0]  # access first character, which is colour and the turn of that player
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    # if piece == 'P':
                    #     self.get_pawn_moves(r, c, moves)
                    # if piece == 'R':
                    #     self.get_rook_moves(r, c, moves)
                    # if piece == 'B':
                    #     self.get_bishop_moves(r, c, moves)
                    # if piece == 'N':
                    #     self.get_knight_moves(r, c, moves)
                    # if piece == 'Q':
                    #     self.get_queen_moves(r, c, moves)
                    # if piece == 'K':
                    #     self.get_king_moves(r, c, moves)

                    # or using Java-style switch statements
                    # noinspection PyArgumentList
                    self.move_functions[piece](r, c, moves) # calls the apt move function
        return moves

#################################### PIECE LOGIC ####################################

    def get_pawn_moves(self, r, c, moves):
        '''
        Get pawn moves for pawn located at r, c and add these moves to the list
        '''
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.whiteToMove:
            move_amount = -1
            init_row = 6
            back_row = 0
            enemy_colour = 'b'

        else:
            move_amount = 1
            init_row = 1
            back_row = 7
            enemy_colour = 'w'
        is_pawn_promotion = False

        # check if the square in front is empty, we go, if the next too, then we can do 2
        if self.board[r + move_amount][c] == '--':
            if not piece_pinned or pin_direction == (move_amount, 0):  # can go in direction of pin
                if r+move_amount == back_row:  # promotion
                    is_pawn_promotion = True
                moves.append(Move((r, c), (r+move_amount, c), self.board, is_pawn_promotion=is_pawn_promotion))
                if r == init_row and self.board[r+2*move_amount][c] == '--':  # 2 squares ahead
                    moves.append(Move((r, c), (r+2*move_amount, c), self.board))

        # captures to the left, make sure we don't go off the board
        if c - 1 >= 0:
            if not piece_pinned or pin_direction == (move_amount, -1):
                if self.board[r+move_amount][c - 1][0] == enemy_colour:
                    if r + move_amount == back_row:
                        is_pawn_promotion = True
                    moves.append(Move((r, c), (r + move_amount, c - 1), self.board, is_pawn_promotion=is_pawn_promotion))
                if (r + move_amount, c - 1) == self.en_passant_is_poss:
                    moves.append(Move((r, c), (r + move_amount, c - 1), self.board, enPassant=True))


        # captures to the right, make sure we don't go off the board
        if c + 1 <= 7:
            if not piece_pinned or pin_direction == (move_amount, 1):
                if self.board[r+move_amount][c + 1][0] == enemy_colour:
                    if r + move_amount == back_row:
                        is_pawn_promotion = True
                    moves.append(Move((r, c), (r+move_amount, c + 1), self.board, is_pawn_promotion=is_pawn_promotion))
                if (r+move_amount, c+1) == self.en_passant_is_poss:
                    moves.append(Move((r, c), (r+move_amount, c+1), self.board, enPassant=True))

            # add pawn promotions later and en-passant



    def get_king_moves(self, r, c, moves):
        '''
        Get king moves for king located at r, c and add these moves to the list
        '''
        row_moves = (-1, -1, -1, 0, 0, 1, 1, 1)
        col_moves = (-1, 0, 1, -1, 1, -1, 0, 1)
        ally_colour = 'w' if self.whiteToMove else 'b'
        for i in range(8):
            end_row = r + row_moves[i]
            end_col = c + col_moves[i]
            if 0 <= end_row < 8 and 0 <= end_col < 8:  # we are on the board
                end_piece = self.board[end_row][end_col]
                if end_piece[0] != ally_colour:  # must be done this way, if same colour and '--', eats own pieces
                    # poner el rey en la casilla extrema y buscar pinchas y jaques
                    if ally_colour == 'w':
                        self.white_king_loc = (end_row, end_col)
                    else:
                        self.black_king_loc = (end_row, end_col)
                    in_check, pins, checks = self.check_for_pins_and_checks()
                    if not in_check:
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    # volver el rey a su posicion original
                    if ally_colour == 'w':
                        self.white_king_loc = (r, c)
                    else:
                        self.black_king_loc = (r, c)

        self.get_castle_moves(r, c, moves, ally_colour)

    def get_castle_moves(self, r, c, moves, ally_colour):
        '''
        Generate all valid castle moves for the king at (r,c) then add them to the list
        '''
        in_check = self.square_under_attack(r, c, ally_colour)
        if in_check:
            print('oof')
            return  # no pasa nada, can't castle when in check
        if (self.whiteToMove and self.current_castle_rights.wks) or (not self.whiteToMove and self.current_castle_rights.bks):
            self.get_kingside_castle_moves(r, c, moves)
        if (self.whiteToMove and self.current_castle_rights.wqs) or (not self.whiteToMove and self.current_castle_rights.bqs):
            self.get_queenside_castle_moves(r, c, moves)

    def get_kingside_castle_moves(self, r, c, moves):
        if self.board[r][c+1] == '--' and self.board[r][c+2] == '--':
            if not self.square_under_attack(r, c+1) and not self.square_under_attack(r, c+2):
                moves.append(Move((r, c), (r, c+2), self.board, is_castle_move=True))

    def get_queenside_castle_moves(self, r, c, moves):
        if self.board[r][c - 1] == '--' and self.board[r][c - 2] == '--' and self.board[r][c-3] == '--':
            if not self.square_under_attack(r, c-1) and not self.square_under_attack(r, c-2):
                moves.append(Move((r, c), (r, c-2), self.board, is_castle_move=True))


    def get_rook_moves(self, r, c, moves):
        '''
        Get rook moves for rook located at r, c and add these moves to the list
        '''
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != 'Q':  # can't remoce queen from pin on rook moves, only on bishop moves
                    self.pins.remove(self.pins[i])  # comment this to see the difference in bamboozle
                break

        directions = ((0, 1), (0, -1), (1, 0), (-1, 0))
        enemy_colour = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for step in range(1, 8):
                end_row = r + d[0] * step
                end_col = c + d[1] * step
                if 0 <= end_row < 8 and 0 <= end_col < 8:  # we are on the board
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == '--':
                            moves.append(Move((r, c), (end_row, end_col), self.board))
                        elif end_piece[0] == enemy_colour:
                            moves.append(Move((r, c), (end_row, end_col), self.board))
                            break  # comment out and rooks can jump over ENEMY pieces only
                        else:  # own colour piece
                            break
                else:  # fall off board
                    break


    def get_bishop_moves(self, r, c, moves):
        '''
        Get bishop moves for bishop located at r, c and add these moves to the list
        '''
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])  # comment this to see the difference in bamboozle
                break
        directions = ((1, 1), (-1, -1), (1, -1), (-1, 1))
        enemy_colour = 'b' if self.whiteToMove else 'w'
        for d in directions:
            for step in range(1, 8):
                end_row = r + d[0] * step
                end_col = c + d[1] * step
                if 0 <= end_row < 8 and 0 <= end_col < 8:  # we are on the board
                    if not piece_pinned or pin_direction == d or pin_direction == (-d[0], -d[1]):
                        end_piece = self.board[end_row][end_col]
                        if end_piece == '--':
                            moves.append(Move((r, c), (end_row, end_col), self.board))
                        elif end_piece[0] == enemy_colour:
                            moves.append(Move((r, c), (end_row, end_col), self.board))
                            break  # comment out and bishop can jump over ENEMY pieces only
                        else:  # own colour piece
                            break
                else:  # fall off board
                    break
           

    def get_knight_moves(self, r, c, moves):
        '''
        Get knight moves for knight located at r, c and add these moves to the list
        '''
        piece_pinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piece_pinned = True
                self.pins.remove(self.pins[i])  # comment this to see the difference in bamboozle
                break

        destinations = ((2, 1), (2, -1), (-2, -1), (-2, 1), (1, -2), (1, 2), (-1, 2), (-1, -2))
        ally_colour = 'w' if self.whiteToMove else 'b'
        for d in destinations:
            end_row = r + d[0]
            end_col = c + d[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:  # we are on the board
                if not piece_pinned:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] != ally_colour:
                        moves.append(Move((r, c), (end_row, end_col), self.board))





    def get_queen_moves(self, r, c, moves):
        '''
        Get queen moves for queen located at r, c and add these moves to the list
        '''
        self.get_bishop_moves(r, c, moves)
        self.get_rook_moves(r, c, moves)


    def update_castle_rights(self, move):
        if move.piece_moved == 'wK':
            self.current_castling_right.wks = False
            self.current_castling_right.wqs = False
        elif move.piece_moved == 'bK':
            self.current_castling_right.bks = False
            self.current_castling_right.bqs = False
        elif move.piece_moved == 'wR':
            if move.start_row == 7:
                if move.start_col == 0:  # left rook
                    self.current_castling_right.wqs = False
                elif move.start_col == 7:  # right rook
                    self.current_castling_right.wks = False
        elif move.piece_moved == 'bR':
            if move.start_row == 0:
                if move.start_col == 0:  # left rook
                    self.current_castling_right.bqs = False
                elif move.start_col == 7:  # right rook
                    self.current_castling_right.bks = False



    def get_valid_moves(self):
        '''
        All moves that consider checks (can't know until I know all possible next moves, checking for checks). Filters.
        '''
        # temp_en_passant = self.en_passant_is_poss  # our copy, tuples are immutable
        # temp_castle_rights = CastleRights(self.current_castling_right.wks, self.current_castling_right.bks,
        #                                         self.current_castling_right.wqs, self.current_castling_right.bqs)  #copy the current castling
        # # NAIVE WAY
        # # 1. generate all poss moves
        # moves = self.get_poss_moves()
        # if self.whiteToMove:
        #     self.get_castle_moves(self.white_king_loc[0], self.white_king_loc[1], moves)
        # else:
        #     self.get_castle_moves(self.black_king_loc[0], self.black_king_loc[1], moves)
        # # 2. make all the moves
        # for i in range(len(moves) - 1, -1, -1):  # iterate through list backwards, to avoid wrong shifting of indices
        #     self.make_move(moves[i])
        #     # 3. generate all opponent's moves, done in in_check and quare_under_attach
        #     # 4. for each of these, see if they leave king under attack
        #     self.whiteToMove = not self.whiteToMove
        #     if self.in_check:
        #         moves.remove(moves[i])  # 5. if they do attack, it's an invalid move
        #     self.whiteToMove = not self.whiteToMove
        #     self.undo_move()  # undo_move swaps move once so parity is even (make_moce cancels out with undo_move)
        # if len(moves) == 0:
        #     if self.in_check:
        #         self.checkmate = True
        #         print('DEATH')
        #     else:
        #         self.stalemate = True
        #         print('STALEDEATH')
        # else:
        #     self.checkmate = False
        #     self.stalemate = False  # if we undo after checkmate, they will now be false again
        #
        # return moves
        moves = []
        self.in_check, self.pins, self.checks = self.check_for_pins_and_checks()
        if self.whiteToMove:
            king_row = self.white_king_loc[0]
            king_col = self.white_king_loc[1]
        else:
            king_row = self.black_king_loc[0]
            king_col = self.black_king_loc[1]
        if self.in_check:
            if len(self.checks) == 1:  # only 1 check, block it or move king
                moves = self.get_poss_moves()
                # to block we move a piece in the line of fire
                check = self.checks[0]
                check_row = check[0]
                check_col = check[1]
                piece_checking = self.board[check_row][check_col]  # enemy piece causing the check
                valid_squares = []  # squares that pieces can move to
                # if knight checking, must capture it or move king
                if piece_checking[1] == 'N':
                    valid_squares = [(check_row, check_col)]
                else:
                    for i in range(1, 8):
                        valid_square = (king_row + check[2] * i, king_col + check[3] * i)  # check[2] and check[3] are check directions
                        valid_squares.append(valid_square)
                        if valid_square[0] == check_row and valid_square[1] == check_col:
                            break

                    # improving efficiency by geting rid of moves that don't block the check or move the king
                    for i in range(len(moves) - 1, -1, -1):  # backwards through iterations to avoid index shifts
                        if moves[i].piece_moved[1] != 'K':  # move doesn't move king so it must block or capture?
                            if not (moves[i].end_row, moves[i].end_col) in valid_squares:  # move doesn't block check or capture piece
                                moves.remove(moves[i])
            else:  # double check, king must move
                self.get_king_moves(king_row, king_col, moves)
        else:  # not in check so all moves are okay
            moves = self.get_poss_moves()

        if len(moves) == 0:
            if self.in_check:
                self.checkmate = True
                print('DEATH')
            else:
                self.stalemate = True
                print('STALEDEATH')
        else:
            self.checkmate = False
            self.stalemate = False

        # self.get_castle_moves(r, c, moves, ally_colour)
        # self.en_passant_is_poss = temp_en_passant  # resets. This is to save the value for when we generate moves. only for native way
        # self.current_castling_right = temp_castle_rights
        return moves



    def check_for_pins_and_checks(self):
        '''
        If player is in check, returns list of pins and checks
        '''
        pins = []
        checks = []
        in_check = False
        if self.whiteToMove:
            enemy_colour = 'b'
            ally_colour = 'w'
            start_row = self.white_king_loc[0]
            start_col = self.white_king_loc[1]
        else:
            enemy_colour = 'w'
            ally_colour = 'b'
            start_row = self.black_king_loc[0]
            start_col = self.black_king_loc[1]
        # check outwards from king for pins and checks, trakcing pins. ASTERISK
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))  # rook, then bishop
        for j in range(len(directions)):
            d = directions[j]
            poss_pin = ()  # resets possible pins
            for i in range(1, 8):
                end_row = start_row + d[0] * i
                end_col = start_col + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] == ally_colour and end_piece[1] != 'K':  # phantom king
                        if poss_pin == ():  # 1st allied piece could be pinned
                            poss_pin = (end_row, end_col, d[0], d[1])  # variable not called can indicate indentation errors
                        else:  # 2nd allied piece, no longer pinned and no check poss in this direction
                            break
                    elif end_piece[0] == enemy_colour:
                        type = end_piece[1]  # reaction depends on this
                        # 5 components to this complex conditional
                        # 1) orthogonally from king and enemy piece is a rook
                        # 2) diagonally from king and enemy piece is a bishop
                        # 3) 1 square diagonally from king and and enemy piece is a pawn
                        # 4) any direction and piece is a queen
                        # 5) any direction 1 square away and piece is a king (so king can't move into other king's space
                        if (0 <= j <= 3 and type == 'R') or \
                                (4 <= j <= 7 and type == 'B') or \
                                (i == 1 and type == 'P' and ((enemy_colour == 'w' and 6 <= j <= 7) or (enemy_colour == 'b' and 4 <= j <= 5))) or \
                                (type == 'Q') or (i == 1 and type == 'K'):
                            if poss_pin == ():  # no piece blocking, so check
                                in_check = True
                                checks.append((end_row, end_col, d[0], d[1]))
                                break
                            else:  # piece blocking so pin
                                pins.append(poss_pin)
                                break
                        else:  #piezas enemigas no aplican jaque. Castillo en una diagonal por ejemplo
                            break
                else:  # mirando mas alla de la tabla
                    break
        # buscar jaques de caballos
        knight_moves = ((-2, 1), (-2, -1), (2, 1), (2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2))
        for m in knight_moves:
            end_row = start_row + m[0]
            end_col = start_col + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] == enemy_colour and end_piece[1] == 'N':  # caballo enemigo ataca el rey
                    in_check = True
                    checks.append((end_row, end_col, m[0], m[1]))
        return in_check, pins, checks


    def in_check(self):  # we could put this into get_valid_moves but having it as a separate func allows usage elsewhe
        '''
        Determines if player is in check
        '''
        if self.whiteToMove:
            return self.square_under_attack(self.white_king_loc[0], self.white_king_loc[1])
        else:
            return self.square_under_attack(self.black_king_loc[0], self.black_king_loc[1])

    def square_under_attack(self, r, c, ally_colour):
        '''
        Determine if square (r, c) can be attacked by opponent
        '''
        self.whiteToMove = not self.whiteToMove  # switch turns
        opponent_moves = self.get_poss_moves()
        self.whiteToMove = not self.whiteToMove  # switch turns back
        for move in opponent_moves:
            if move.end_row == r and move.end_col == c:  # square is under attack
                return True
        return False

class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move():  # nested classes exist, this is not recommended

    # maps keys to values {key : value}
    ranks_to_rows = {'1': 7, '2': 6, '3': 5, '4': 4,
                     '5': 3, '6': 2, '7': 1, '8': 0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}
    files_to_cols = {'h': 7, 'g': 6, 'f': 5, 'e': 4,
                     'd': 3, 'c': 2, 'b': 1, 'a': 0}
    cols_to_files = {v: k for k, v in files_to_cols.items()}


    def __init__(self, start_sq, end_sq, board, enPassant=False, is_pawn_promotion=False, is_castle_move = False):  # optional parameters
        self.start_row = start_sq[0]
        self.start_col = start_sq[1]
        self.end_row = end_sq[0]
        self.end_col = end_sq[1]
        # tracking what piece was and what was captured
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]

        # pawn promotion stuff
        # self.is_pawn_promotion = False
        # if (self.piece_moved == 'wP' and self.end_row == 0) or (self.piece_moved == 'bP' and self.end_row == 7):
        #     self.is_pawn_promotion = True
        #     print('Pawn promoted')
        # OR neater
        self.is_pawn_promotion = is_pawn_promotion

        #en passant stuff
        self.enPassant = enPassant
        if enPassant:
            self.piece_captured = 'bP' if self.piece_moved == 'wP' else 'wP'

        # castling stuff
        self.is_castle_move = is_castle_move

        self.moveID = self.start_row*1000 + self.start_col*100 + self.end_row*10 + self.end_col

    '''
    Overriding the equal method. Since we are using a class, we have to do this.
    '''
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False


    def get_chess_notation(self):
        # add real chess notation here
        return self.get_rank_file(self.start_row, self.start_col) + ' -> ' + \
               self.get_rank_file(self.end_row, self.end_col)


    def get_rank_file(self, r, c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]
