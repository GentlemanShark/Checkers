'''
File: checkers.py
Author: Stuart Trappe
Course: CSC 120
Purpose: This file contains a checkers class that contains several methods
         for game operations, printing, and move validation. It can check
         several aspects of game status (active player, if the game is over,
         amount of each color left) and prints out the board in a readable way.
'''


import copy
import sys

class Checkers():
    '''
    This class represents one point in the game. It can be initalized with
    either a default starting game or with a custom board state such as for
    storing a game in progress. It represents the board with a 2D array
    filled with 'tiles' or game squares that can either be a red
    checker/king, a black checker/king, or a blank.

    It includes several getters from the current player to a user readable
    output to the amount of pieces left. The most complex method is the
    do_move()method as it performs several checks to see if a move is valid
    and what needs to be done to make that move happen. A valid move will
    return a new Checkers class with the board_state changed to include the
    move.
    '''
    def __init__(self, board_state = 'default'):
        '''
        This function creates a new board_array with either the default board
        or a custom inputted one.
        Arguments: board_state's first character represents the current
        player and every line after that represents a row on the board with
        periods meaning blank.
        '''
        if board_state == 'default':  # Starting game
            self.board_state = 'r r.r.r.r. .r.r.r.r r.r.r.r. ........ '
            self.board_state += '........ .b.b.b.b b.b.b.b. .b.b.b.b'
            self.board_text = self.board_state.split()
        else:
            self.board_text = board_state.split()
            assert len(self.board_text) == 9
            assert self.board_text[0] in ['r', 'b']

            for row_num in range(1, len(self.board_text)):
                assert len(self.board_text[row_num]) == 8
                for tile in self.board_text[row_num]:
                    assert tile in ['r', 'b', 'R', 'B', '.']

            self.board_state = board_state

        self.current_player = self.board_text[0]  # Indicates starting player
        self.board_text.pop(0)  # Ignore first character

        self.board_array = []  # Initialize blank array
        for row in self.board_text:
            temp_row = []
            for tile in row:
                temp_row.append(tile)
            self.board_array.append(temp_row)
        self.board_array.reverse()  # Flips the board



    def __str__(self):
        '''
        If checkers class is printed, it returns the board_state
        '''
        return self.board_state

    def get_cur_player(self):
        '''
        Returns color of who's turn it is
        '''
        if self.current_player == 'r':
            return 'red'
        else:
            return 'black'

    def get_square(self, x, y):
        '''
        When given x and y coordinates, it returns value at a space
        '''
        assert type(x) == int and type(y) == int  # Input validation
        assert x >= 0 and x <= 7  # Check if within bounds
        assert y >= 0 and y <= 7
        return self.board_array[7-y][x]  # -7 to account for flipped board

    def get_printable_string(self):
        '''
        Returns a string of a text based graphical output of the board. It
        substitutes periods for blank spaces and shows row numbers and column
        letters.
        '''
        output = ''  # String to be returned
        row_num = 8
        for row in self.board_array:
            output += '+---+---+---+---+---+---+---+---+\n'
            output += str(row_num)
            for space in row:
                if space == '.':  # Substitute period for a blank
                    output += '   |'
                else:
                    output += ' ' + space + ' |'
            output += '\n'
            row_num -= 1  # Deincrement row number
        output += '+-a-+-b-+-c-+-d-+-e-+-f-+-g-+-h-+'
        return output

    def get_piece_count(self, color):
        '''
        Given a color, returns the number of them remaining with
        a tuple of normal pieces and kings. Color is 'r' or 'b'
        '''
        assert color in ['r', 'b']
        piece_counter = 0
        king_counter = 0
        for row in self.board_array:
            for space in row:
                if space == color:  # Count pieces
                    piece_counter += 1
                elif space == color.capitalize():  # Count kings
                    king_counter += 1
        return (piece_counter, king_counter)

    def is_game_over(self):
        '''
        Determines if one side has won or not. Returns true if
        a color has no remaining pieces left.
        '''
        red_counter = 0
        black_counter = 0
        for row in self.board_array:
            for space in row:
                if space == 'r':
                    red_counter += 1  # Number of red pieces left
                else:
                    black_counter += 1  # Number of black pieces left
        if red_counter == 0 or black_counter == 0:
            return True
        else:
            return False

    def do_move(self, frm, to):
        '''
        Takes in an input of a from and to location in rank and file
        format and returns a new Checkers object with the move made
        assuming it is valid. If it is not, it returns nothing. It
        also includes several checks to verify that every aspect of
        a move is valid.
        '''
        # asserts inputs are valid
        assert len(frm) == 2 and len(to) == 2
        assert frm[0] in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        assert to[0] in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        assert int(frm[1]) and int(to[1])
        assert int(frm[1]) >= 1 and int(frm[1]) <= 8
        assert int(to[1]) >= 1 and int(to[1]) <= 8

        self.need_to_be_knighted = False  # Set to True if at end of board
        self.captured = None  # Captured piece from jumping over

        frm_coord = (ord(frm[0]) - 97, int(frm[1]) - 1)  # convert character
        to_coord = (ord(to[0]) - 97, int(to[1]) - 1)
        if self.get_square(frm_coord[0],frm_coord[1]) not in ['r','b','R','B']:
            return None
        elif self.get_square(to_coord[0],to_coord[1]) in ['r','b','R','B']:
            return None
        elif not self.moving_own_piece(frm_coord):
            return None
        elif not self.is_diagonal_move(frm_coord, to_coord):
            return None
        elif not self.is_one_or_two_step_move(frm_coord, to_coord):
            return None
        elif self.captured!=None and not self.is_opposite_suit(self.captured):
            return None
        elif not self.is_correct_direction(frm_coord, to_coord):
            return None
        else:
            # New array is created after pieces are moved
            new_board_array = self.move_pieces(frm_coord, to_coord,
            self.need_to_be_knighted, self.captured)
            self.switch_player()  # Change current player
            new_board_state = self.board_to_string(new_board_array)
            return Checkers(new_board_state)  # Builds new object

    def moving_own_piece(self, frm_coord):
        '''
        Takes a from coordinate and ensures that a player is moving their
        own team's color on their turn. Returns true if that is the case.
        '''
        if self.get_cur_player() == 'red':
            if self.get_square(frm_coord[0], frm_coord[1]) in ['r', 'R']:
                return True
            else:
                return False
        else:
            if self.get_square(frm_coord[0], frm_coord[1]) in ['b', 'B']:
                return True
            else:
                return False

    def is_diagonal_move(self, frm_coord, to_coord):
        '''
        Takes a from and to coordinate to determine if moves are diagnoal
        as required by checkers. Returns true if that is the case.
        Displacement represents the distance between coordinates.
        '''
        displacement = (abs(frm_coord[0] - to_coord[0]), abs(frm_coord[0] - to_coord[0]))
        if displacement[0] == displacement[1]:  # Only diagnoal if equal
            return True

    def is_one_or_two_step_move(self, frm_coord, to_coord):
        '''
        Takes a from and to coordinate to determine if a move either only
        moves once or makes a jump. It also determines which piece to capture
        if it is jumped over.
        '''
        # Displace is absolute value as it is just distance between points
        displacement = (abs(frm_coord[0] - to_coord[0]), abs(frm_coord[0] - to_coord[0]))
        if displacement[0] == 1:  # Only moved over 1 tile
            return True
        elif displacement[0] == 2:
            # Captured is the middle coord between to and from points
            self.captured = (int((frm_coord[0] + to_coord[0])/2), int((frm_coord[1]+to_coord[1])/2))
            return True

    def is_opposite_suit(self, piece_coord):
        '''
        Takes in a coordinate for a piece on the board and determines if it
        is on the opposing team of the current player. Returns true if that
        is the case.
        '''
        if self.get_cur_player() == 'red':
            if self.get_square(piece_coord[0], piece_coord[1]) in ['b', 'B']:
                return True
            else:
                return False
        else:
            if self.get_square(piece_coord[0], piece_coord[1]) in ['r', 'R']:
                return True
            else:
                return False

    def is_correct_direction(self, frm_coord, to_coord):
        '''
        Takes a from and too cordinate to determine that pieces are being
        moved in the correct direction. Red pieces move up the board and
        black pieces down the board with the exception of kings. It also
        determines if a piece has reached the end of the board and thus
        needs to be knighted. Returns true if it is the correct direction.
        '''
        if self.get_square(frm_coord[0], frm_coord[1]) == 'r':  # Move upward
            if to_coord[1] > frm_coord[1]:
                if to_coord[1] == 7:  # Reached end of board
                    self.need_to_be_knighted = True
                return True
            else:
                return False
        elif self.get_square(frm_coord[0], frm_coord[1]) == 'b':  # Move downward
            if to_coord[1] < frm_coord[1]:
                if to_coord[1] == 0:  # Reached end of board
                    self.need_to_be_knighted = True
                return True
            else:
                return False
        else:  # Otherwise is a king
            return True


    def move_pieces(self, frm_coord, to_coord, need_to_be_knighted, captured):
        '''
        Takes in from and to coordinate, a boolean for knighting status, and if
        a piece was captured. Returns a new board array with the pieces moved.
        '''
        # Deepcopy prevents current board from being modified
        new_board = copy.deepcopy(self.board_array)
        if need_to_be_knighted:  # Capitalize letter and place (e.g. b -> B)
            new_board[7-to_coord[1]][to_coord[0]] = self.get_square(frm_coord[0], frm_coord[1]).capitalize()
        else:  # Move piece on board
            new_board[7-to_coord[1]][to_coord[0]] = self.get_square(frm_coord[0], frm_coord[1])
        if captured != None:
            new_board[7-captured[1]][captured[0]] = '.' # Removed from board
        new_board[7-frm_coord[1]][frm_coord[0]] = '.'  # Remove from coordinate
        return new_board

    def board_to_string(self, board):
        '''
        Converts a board array into a board string. Essentially adds up rows
        from an board into a string and heads it with the new current player.
        '''
        temp_board = board
        string = ''  # String to be returned
        string += self.current_player  # Header
        temp_board.reverse()  # Flips board
        for row in temp_board:
            string += ' '
            for tile in row:
                string += tile
        return string

    def switch_player(self):
        '''
        Switches the current player (e.g. red -> black)
        '''
        if self.get_cur_player() == 'red':
            self.current_player = 'b'
        else:
            self.current_player = 'r'

def main():
    '''
    30 tests to tell if methods function correctly and assertions
    catch errors. Returns the number of passed tests if less than
    all are passed and states if all are passed.
    '''
    test_passes = 0
    try:
        board1 = Checkers()
        test_passes += 1
    except:
        print('error 1')
    try:
        board1 = Checkers('r r.r.r.r. .r.r.r.r r.r.r.r. ........ ........ .b.b.b.b b.b.b.b. .b.b.b.b')
        test_passes += 1
    except:
        print('error 2')
    try:
        board1 = Checkers('1 r.r.r.r. .r.r.r.r r.r.r.r. ........ ........ .b.b.b.b b.b.b.b. .b.b.b.b')
        print('error 3')
    except AssertionError:
        test_passes += 1
    try:
        board1 = Checkers('1 r.r.r.r. r.r.r.r. .r.r.r.r r.r.r.r. ........ ........ .b.b.b.b b.b.b.b. .b.b.b.b')
        print('error 4')
    except AssertionError:
        test_passes += 1
    try:
        board1 = Checkers('1 w.r.r.r. .r.r.r.r r.r.r.r. ........ ........ .b.b.b.b b.b.b.b. .b.b.b.b')
        print('error 5')
    except AssertionError:
        test_passes += 1
    try:
        word = str(board1)
        if word == 'r r.r.r.r. .r.r.r.r r.r.r.r. ........ ........ .b.b.b.b b.b.b.b. .b.b.b.b':
            test_passes += 1
    except:
        print('error 6')
    try:
        if board1.get_cur_player() in ['red', 'black']:
            test_passes += 1
    except AssertionError:
        print('error 7')
    try:
        board1.get_square(1, 1)
        test_passes += 1
    except AssertionError:
        print('error 8')
    try:
        board1.get_square(-1, -1)
        print('error 9')
    except AssertionError:
        test_passes += 1
    try:
        board1.get_square(11, 11)
        print('error 10')
    except AssertionError:
        test_passes += 1
    try:
        board1.get_square('blue', 11)
        print('error 11')
    except AssertionError:
        test_passes += 1
    try:
        word = board1.get_printable_string()
        test_passes += 1
    except:
        print('error 12')
    try:
        amount = board1.get_piece_count('r')
        test_passes += 1
    except:
        print('error 13')
    try:
        amount = board1.get_piece_count('b')
        test_passes += 1
    except:
        print('error 14')
    try:
        amount = board1.get_piece_count('g')
        print('error 15')
    except AssertionError:
        test_passes += 1
    try:
        if not board1.is_game_over():
            test_passes += 1
    except:
        print('error 16')
    try:
        if not board1.is_game_over():
            test_passes += 1
    except:
        print('error 17')
    try:
        new_board = board1.do_move('a3', 'b4')
        test_passes += 1
    except:
        print('error 18')
    try:
        new_board = board1.do_move('a3mas', 'b4')
        print('error 19')
    except AssertionError:
        test_passes += 1
    try:
        new_board = board1.do_move('z3', 'b4')
        print('error 20')
    except AssertionError:
        test_passes += 1
    try:
        new_board = board1.do_move('a3', 'z4')
        print('error 21')
    except AssertionError:
        test_passes += 1
    try:
        new_board = board1.do_move('aa', 'z4')
        print('error 22')
    except AssertionError:
        test_passes += 1
    try:
        new_board = board1.do_move('a0', 'z4')
        print('error 23')
    except AssertionError:
        test_passes += 1
    try:
        new_board = board1.do_move('a9', 'z4')
        print('error 24')
    except AssertionError:
        test_passes += 1
    try:
        new_board = board1.do_move('a3', 'z0')
        print('error 25')
    except AssertionError:
        test_passes += 1
    try:
        new_board = board1.do_move('a3', 'z9')
        print('error 26')
    except AssertionError:
        test_passes += 1
    try:
        board1.moving_own_piece((0,0))
        test_passes += 1
    except:
        print('error 27')
    if(board1.moving_own_piece((2,7))) == False:
        test_passes += 1
    else:
        print('error 28')
    try:
        board1.is_diagonal_move((2,3), (0,4))
        test_passes += 1
    except:
        print('error 29')
    try:
        board1.switch_player()
        test_passes += 1
    except:
        print('error 30')

    if test_passes == 30:
        print('UNITTEST COMPLETE. NO FAILURES DETECTED.')
    else:
        print('Unittest complete. ' + str(test_passes) + ' out of 30 tests passed.')


if __name__ == "__main__":
    main()