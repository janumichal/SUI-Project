import logging
from random import shuffle
import numpy as np
import random
from copy import deepcopy, copy

from ..utils import possible_attacks, attack_succcess_probability, probability_of_holding_area

from dicewars.client.ai_driver import BattleCommand, EndTurnCommand


class FinalAI:
    """xdufko02 player agent
    """

    def __init__(self, player_name, board, players_order):
        """
        Parameters
        ----------
        game : Game
        """
        self.player_name = player_name
        self.logger = logging.getLogger('AI')
        self.order = players_order
        self.turns = []

    def ai_turn(self, board, nb_moves_this_turn, nb_turns_this_game, time_left):
        """AI agent's turn
        """
        if len(self.turns) == 0:
            self.turns = self.expectiMiniMax(deepcopy(board), self.player_name, True)
        while len(self.turns) > 0:
            turn = self.turns.pop(0)
            real_source = board.get_area(turn[0].get_name())
            if real_source.get_dice() <= 1 or real_source.get_owner_name() != self.player_name:
                continue
            return BattleCommand(turn[0].get_name(), turn[1].get_name())
        return EndTurnCommand()
        
    def expectiMiniMax(self, board, current_player, first):
        if current_player == self.player_name and first == False:
            return self.get_score(board, self.player_name)
        if current_player == self.player_name:
            probabilities = []
            turns = []
            for turn in range(3):
                real_turns = []
                new_board = deepcopy(board)
                for x in range(3):
                    attacks = self.get_good_attacks(new_board, current_player)
                    if len(attacks) == 0:
                        break
                    random_attack = random.choice(attacks)
                    # print("DICE ",random_attack[0].get_dice(), " ", random_attack[1].get_dice())

                    self.capture_node(random_attack[0], random_attack[1])
                    real_turns.append(random_attack)

                probabilities.append(self.expectiMiniMax(new_board, self.get_next_player(current_player, new_board), False))
                turns.append(real_turns)
                if len(probabilities) == 0:
                    return []
                return_values = turns[np.argmax(probabilities)]
                # for val in return_values:
                #     print("DICE ",val[0].get_dice(), " ", val[1].get_dice())

                return return_values
        else:
            new_board = deepcopy(board)
            for x in range(3):
                attacks = self.get_good_attacks(new_board, current_player)
                if len(attacks) == 0:
                    break
                random_attack = random.choice(attacks)

                self.capture_node(random_attack[0], random_attack[1])
            return self.expectiMiniMax(new_board, self.get_next_player(current_player, new_board), False)

        

    def capture_node(self, source, target):
        target.set_dice(source.get_dice() - 1)
        target.set_owner(source.get_owner_name())
        source.set_dice(1)

    def get_score(self, board, current_player):
        players_regions = board.get_players_regions(current_player, skip_area=None)
        max_size = 0
        for region in players_regions:
            max_size = max(max_size, len(region))
        # max_region_size = max(len(region) for region in players_regions)
        # score = 0
        # all_player_areas = board.get_player_areas(current_player)
        # for area in all_player_areas:
        #     score += probability_of_holding_area(board, area.get_name(), area.get_dice(), current_player)
        # return score
        return max_size
        # return len(all_player_areas)

    def get_next_player(self, current_player, board):
        count = 1
        while True:
            next_player = self.order[(self.order.index(current_player) + count)%len(self.order)]
            if len(board.get_player_areas(next_player)) > 0:
                break
            count+=1
        # print("x: ", next_player, " ", current_player)
        return next_player
    
    def get_good_attacks(self, board, player):
        attacks = list(possible_attacks(board, player))
        return list(filter(lambda attack: attack[0].get_dice() > attack[1].get_dice(), attacks))