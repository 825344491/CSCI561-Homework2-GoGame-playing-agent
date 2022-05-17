from cmath import inf
from read import readInput
from write import writeOutput

from host import GO
from random_player import RandomPlayer

class MinMaxPlayer():
    def __init__(self):
        self.type = 'minmax'
        self.search_depth = 4

    def get_input(self, go, piece_type):
        '''
        Get one input.

        :param go: Go instance.
        :param piece_type: 1('X') or 2('O').
        :return: (row, column) coordinate of input.
        '''        
        possible_placements = []
        for i in range(go.size):
            for j in range(go.size):
                if self.good_action(i, j, go, piece_type) and go.valid_place_check(i, j, piece_type, test_check = True):
                    possible_placements.append((i,j))

        if go.n_move < 2 and go.valid_place_check(int(go.size/2), int(go.size/2), piece_type, test_check = True):
            return (int(go.size/2), int(go.size/2))
        elif not possible_placements:
            return "PASS"
        else:
            self.current_depth = go.n_move
            _, action = self.max_value(go, piece_type, -inf, inf, possible_placements, 0, 0)
            return action

    def max_value(self, go, piece_type, alpha, beta, possible_placements, dead_allies, dead_enemies):
        if go.game_end(piece_type) or go.n_move - self.current_depth >= self.search_depth:
            allies_liberty = 0
            enemies_liberty = 0
            for i in range(go.size):
                for j in range(go.size):
                    if go.board[i][j] == piece_type:
                        allies_liberty += self.check_liberty(i, j, go)
                    elif go.board[i][j] == 3 - piece_type:
                        enemies_liberty += self.check_liberty(i, j, go)
            
            allies_utility = allies_liberty + go.score(piece_type) + dead_enemies * 10
            enemies_utility = enemies_liberty + go.score(3 - piece_type) - dead_allies * 16
            utility = allies_utility - enemies_utility
            if piece_type == 2:
                utility += go.komi
            return utility, "PASS"

        # Will there be a case where the game is not end, but there is no possible placement?
        v = -inf
        best_action = "PASS"
        for action in possible_placements:
            next_go = go.copy_board()
            next_go.place_chess(action[0], action[1], piece_type)
            next_go.n_move = next_go.n_move + 1
            
            deads = go.find_died_pieces(3 - piece_type)
            dead_enemies += len(deads)
            next_go.died_pieces = next_go.remove_died_pieces(3 - piece_type) # Remove the dead pieces of opponent
            
            next_possible_placements = []
            for i in range(next_go.size):
                for j in range(next_go.size):
                    if self.good_action(i, j, next_go, 3 - piece_type) and next_go.valid_place_check(i, j, 3 - piece_type, test_check = True):
                        next_possible_placements.append((i,j))
            
            next_v, _ = self.min_value(next_go, 3 - piece_type, alpha, beta, next_possible_placements, dead_enemies, dead_allies)
            
            if next_v > v:
                v = next_v
                best_action = action
            
            if v >= beta:
                return v, best_action
            alpha = max(alpha, v)
        return v, best_action
    
    def min_value(self, go, piece_type, alpha, beta, possible_placements, dead_allies, dead_enemies):
        if go.game_end(3 - piece_type) or go.n_move - self.current_depth >= self.search_depth:
            allies_liberty = 0
            enemies_liberty = 0
            for i in range(go.size):
                for j in range(go.size):
                    if go.board[i][j] == piece_type:
                        allies_liberty += self.check_liberty(i, j, go)
                    elif go.board[i][j] == 3 - piece_type:
                        enemies_liberty += self.check_liberty(i, j, go)
            
            allies_utility = allies_liberty + go.score(piece_type) + dead_enemies * 10
            enemies_utility = enemies_liberty + go.score(3 - piece_type) - dead_allies * 16
            utility = allies_utility - enemies_utility
            if piece_type == 2:
                utility += go.komi
            return -1 * utility, "PASS"

        # Will there be a case where the game is not end, but there is no possible placement?
        v = inf
        best_action = "PASS"
        for action in possible_placements:
            next_go = go.copy_board()
            next_go.place_chess(action[0], action[1], piece_type)
            next_go.n_move = next_go.n_move + 1
            
            deads = go.find_died_pieces(3 - piece_type)
            dead_enemies += len(deads)
            next_go.died_pieces = next_go.remove_died_pieces(3 - piece_type) # Remove the dead pieces of opponent
            
            next_possible_placements = []
            for i in range(next_go.size):
                for j in range(next_go.size):
                    if self.good_action(i, j, next_go, 3 - piece_type) and next_go.valid_place_check(i, j, 3 - piece_type, test_check = True):
                        next_possible_placements.append((i,j))
            
            next_v, _ = self.max_value(next_go, 3 - piece_type, alpha, beta, next_possible_placements, dead_enemies, dead_allies)
            if next_v < v:
                v = next_v
                best_action = action
            
            if v <= alpha:
                return v, best_action
            beta = min(beta, v)
        return v, best_action

    def good_action(self, i, j, go, piece_type):
        if go.board[i][j] == 0:
            neighbors = go.detect_neighbor(i, j)
            for neighbor in neighbors:
                if go.board[neighbor[0]][neighbor[1]] == 3 - piece_type:
                    return True
        return False

    def check_liberty(self, i, j, go):
        '''
        Check the number of liberty of a given stone.

        :param i: row number of the board.
        :param j: column number of the board.
        :return: integer indicating the number of liberty the given stone has.
        '''
        count = 0
        
        board = go.board
        ally_members = go.ally_dfs(i, j)
        for member in ally_members:
            neighbors = go.detect_neighbor(member[0], member[1])
            for piece in neighbors:
                # If there is empty space around a piece, it has liberty
                if board[piece[0]][piece[1]] == 0:
                    count += 1
        # If none of the pieces in a allied group has an empty space, it has no liberty
        return count

if __name__ == "__main__":
    N = 5
    # go = GO(N)
    # go.verbose = True
    # player1 = MinMaxPlayer()
    # player2 = RandomPlayer()
    # result = go.play(player1, player2, True)
    piece_type, previous_board, board = readInput(N)
    # print(piece_type)
    # print(previous_board)
    # print(board)
    go = GO(N)
    go.set_board(piece_type, previous_board, board)
    # print(go.board)
    player = MinMaxPlayer()
    action = player.get_input(go, piece_type)
    # print(action)
    writeOutput(action)