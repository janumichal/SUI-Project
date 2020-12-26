import logging
from random import shuffle
import numpy as np
from copy import deepcopy

from ..utils import possible_attacks, attack_succcess_probability, probability_of_holding_area

from dicewars.client.ai_driver import BattleCommand, EndTurnCommand


class FinalAI:
    """xdufko02 player agent

    This agent blabla...
    """

    def __init__(self, player_name, board, players_order):
        """
        Parameters
        ----------
        game : Game
        """
        self.player_name = player_name
        self.logger = logging.getLogger('AI')

    def ai_turn(self, board, nb_moves_this_turn, nb_turns_this_game, time_left):
        """AI agent's turn


        """

        if nb_moves_this_turn > 3:
            return EndTurnCommand()

        depth = 2
        nodes = list(possible_attacks(board, self.player_name))

        if len(nodes) == 0:
            return EndTurnCommand()

        attack_probs = []
        for source, target in nodes:
            attack_dice = source.get_dice()
            defender_dice = target.get_dice()
            attack_probs.append(attack_succcess_probability(attack_dice, defender_dice))

        nodes_scores = []
        for i, (source, target) in enumerate(nodes):
            node_score = attack_probs[i] * self.expectiMiniMax(source, target, attack_probs[i], depth - 1, board)
            nodes_scores.append(node_score)

        node_to_attack = nodes[np.argmax(nodes_scores)]

        return BattleCommand(node_to_attack[0].get_name(), node_to_attack[1].get_name())

    def expectiMiniMax(self, source, target, attack_prob, depth, board):
        if depth == 0:
            return self.get_score(board) * attack_prob

        #do move
        source_area = board.get_area(source.get_name())
        target_area = board.get_area(target.get_name())
        source_area_dice = source_area.get_dice()
        target_area_owner = target_area.get_owner_name()
        target_area_dice = target_area.get_dice()
        target_area.set_owner(self.player_name)
        target_area.set_dice(source_area.get_dice() - 1)
        source_area.set_dice(1)

        nodes = list(possible_attacks(board, self.player_name))

        if len(nodes) == 0:
            score = self.get_score(board) * attack_prob
            #undo move
            target_area.set_owner(target_area_owner)
            target_area.set_dice(target_area_dice)
            source_area.set_dice(source_area_dice)
            return score

        #calculate attack probs
        attack_probs = []
        for source, target in nodes:
            attack_dice = source.get_dice()
            defender_dice = target.get_dice()
            attack_probs.append(attack_succcess_probability(attack_dice, defender_dice))

        nodes_scores = []
        for i, (source, target) in enumerate(nodes):
            nodes_scores.append(self.expectiMiniMax(source, target, attack_probs[i], depth - 1, board))

        #undo move
        target_area.set_owner(target_area_owner)
        target_area.set_dice(target_area_dice)
        source_area.set_dice(source_area_dice)

        return max(nodes_scores) * attack_prob

    def get_score(self, board):
        players_regions = board.get_players_regions(self.player_name, skip_area=None)
        max_region_size = max(len(region) for region in players_regions)

        #players = list(set(area.get_owner_name() for area in board.areas.values()))
        #players.remove(self.player_name)

        #max_region = 0

        #for player in players:
        #    regions = board.get_players_regions(player, skip_area=None)
        #    max_tmp = max(len(region) for region in regions)
        #    if max_tmp > max_region:
        #        max_region = max_tmp

        #probab_holding = probability_of_holding_area(atk_area, target_area)

        #return max_region_size - max_region
        return max_region_size
        #return probab_holding
