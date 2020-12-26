import logging
from random import shuffle
import numpy as np
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

    def ai_turn(self, board, nb_moves_this_turn, nb_turns_this_game, time_left):
        """AI agent's turn
        """
        if nb_moves_this_turn > 3:
            return EndTurnCommand()

        depth = 3
        nodes = list(possible_attacks(board, self.player_name))

        if len(nodes) == 0:
            return EndTurnCommand()

        nodes_scores = []
        for source, target in nodes:
            attack_dice = source.get_dice()
            defender_dice = target.get_dice()
            attack_prob = attack_succcess_probability(attack_dice, defender_dice)
            node_score = self.expectiMiniMax(source, target, attack_prob, board, self.player_name, nb_moves_this_turn, True)
            nodes_scores.append(node_score)

        max_index = np.argmax(nodes_scores)

        # Maybe useless?
        if nodes_scores[np.argmax(nodes_scores)] < 0.1:
            return EndTurnCommand()

        node_to_attack = nodes[max_index]
        return BattleCommand(node_to_attack[0].get_name(), node_to_attack[1].get_name())

    def expectiMiniMax(self, source, target, attack_prob, board, current_player, current_moves, first):
        # Maybe only less than
        if first == False and self.player_name == current_player:
            return self.get_score(board, current_player) * attack_prob
        if current_moves == 4 or target.get_dice() > source.get_dice():
            nodes_scores = []
            nodes_to_attack = list(possible_attacks(board, self.get_next_player(current_player, board)))
            # Next player is playing
            for next_source, next_target in nodes_to_attack:
                attack_prob = attack_succcess_probability(next_source.get_dice(), next_target.get_dice())
                node_score = attack_prob * self.expectiMiniMax(source, target, attack_prob, board, self.get_next_player(current_player, board), 0, False)
                nodes_scores.append(node_score)
            return max(nodes_scores) * attack_prob
            
        #do move
        source_area = source
        target_area = target
        source_area_dice = source_area.get_dice()
        target_area_owner = target_area.get_owner_name()
        target_area_dice = target_area.get_dice()
        target_area.set_owner(current_player)
        
        target_area.set_dice(source_area.get_dice() - 1)
        source_area.set_dice(1)

        nodes = list(possible_attacks(board, self.player_name))

        if len(nodes) == 0:
            score = self.get_score(board, current_player) * attack_prob
            #undo move
            target_area.set_owner(target_area_owner)
            target_area.set_dice(target_area_dice)
            source_area.set_dice(source_area_dice)
            return score

        #calculate attack probs
        nodes_scores = []
        for source_node, target_node in nodes:
            attack_dice = source_node.get_dice()
            defender_dice = target_node.get_dice()
            attack_prob = attack_succcess_probability(attack_dice, defender_dice)
            node_score = self.expectiMiniMax(source_node, target_node, attack_prob, board, current_player, current_moves + 1, False)
            nodes_scores.append(node_score)
            # if node_score < 0.1:
            #     next_scores = []
            #     nodes_to_attack = list(possible_attacks(board, self.get_next_player(current_player)))
            #     # Next player is playing
            #     print("LEN: ", len(nodes_to_attack))
            #     for next_source, next_target in nodes_to_attack:
            #         attack_prob = attack_succcess_probability(next_source.get_dice(), next_target.get_dice())
            #         next_score = attack_prob * self.expectiMiniMax(source, target, attack_prob, board, self.get_next_player(current_player), 0, False)
            #         # next_scores.append(next_scores)
            #         nodes_scores.append(next_score)
                



        #undo move
        target_area.set_owner(target_area_owner)
        target_area.set_dice(target_area_dice)
        source_area.set_dice(source_area_dice)

        return max(nodes_scores) * attack_prob

    def get_score(self, board, current_player):
        players_regions = board.get_players_regions(current_player, skip_area=None)
        max_region_size = max(len(region) for region in players_regions)
        player_areas_size = len(board.get_player_areas(self.player_name)) // 2

        # max_region_size = max(self.get_region_score(board, region) for region in players_regions)

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
        # return max_region_size + player_areas_size
        return max_region_size
        #return probab_holding
        
    def get_region_score(self, board, region):
        score = 0
        for area_id in region:
            area_score = 0
            area = board.get_area(area_id)
            area_score += area.get_dice()
            if board.is_at_border(area):
                for adj_name in area.get_adjacent_areas():
                    adj_area = board.get_area(adj_name)
                    if adj_area.get_owner_name() != self.player_name and adj_area.get_dice() - 2 > area.get_dice():
                        area_score -= adj_area.get_dice() // 2
            if len(area.get_adjacent_areas()) <= 3:
                area_score += area.get_dice() // 2
                
            score += area_score
            return score

    def get_next_player(self, current_player, board):
        count = 1
        while True:
            next_player = self.order[(self.order.index(current_player) + 1)%len(self.order)]
            if len(board.get_player_areas(next_player)) > 0:
                break
        return next_player