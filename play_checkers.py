#! /usr/bin/env python3

"""Interactive program; allows you to play checkers (no AI).

   Author: Russell Lewis"""

import checkers



def main():
    board = checkers.Checkers()

    while board.is_game_over() == False:
        print()
        print(board)
        print(board.get_printable_string())
        print(board.get_cur_player()+" to move.")
        print()

        move = input("What is the next move?   ").split()
        print()

        if move == ["quit"]:
            print("Game terminated by user.")
            return

        if len(move) != 2 or len(move[0]) != 2 or len(move[1]) != 2:
            print("ERROR: The move must be specified as two words, in the rank-file syntax")
            print()
            input("Hit ENTER to continue...")
            continue

        try:
            new_board = board.do_move(move[0],move[1])
        except AssertionError:
            # if do_move() asserts, then treat this just like a
            # "invalid move" response.
            new_board = None

        if new_board is None:
            print("ERROR: Invalid move.  The Checkers class did not return a new object.")
            print()
            input("Hit ENTER to continue...")
            continue

        board = new_board

    print(board.get_printable_string())
    print()
    print("GAME OVER!")



if __name__ == "__main__":
    main()

