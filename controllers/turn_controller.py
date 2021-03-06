from tinydb import TinyDB, where
from tinydb.table import Document
import uuid
from constants.turn_view_constants import Answer, answers_list
from models.turn import Turn
from controllers.tournament_controller import update_tournament
from controllers.player_controller import get_player_from_id
from controllers.player_controller import get_all_players_as_list

db = TinyDB('data/turns.json')


def create_turn(turn, tournament):
    """Create turn"""
    id = uuid.uuid4().int

    db.insert(
        Document(
            {
                'id': id,
                'name': turn.name,
                'start_time': turn.start_time,
                'end_time': turn.end_time,
                'matchs': turn.matchs,
            },
            doc_id=id))
    turn.id = id


def create_match(turn, tournament):

    player_ids = tournament.players

    players = []
    for id in player_ids:
        player = get_player_from_id(id)
        players.append(player)
    players_sorted = sorted(players, key=lambda x: x.elo)

    length_players = len(players_sorted)

    half_length_players = int(length_players / 2)
    players_first_half = players_sorted[:half_length_players]
    players_second_half = players_sorted[half_length_players:length_players]

    i = 0

    turn.matchs = []
    while i <= (length_players / 2) - 1:

        first_player = players_first_half[i]
        second_player = players_second_half[i]

        tuple_match = ([first_player.id, 0], [second_player.id, 0])

        tournament.encounters[f"{first_player.id}"] = f"{second_player.id}"
        tournament.encounters[f"{second_player.id}"] = f"{first_player.id}"

        if tuple_match not in turn.matchs:
            turn.matchs.append(tuple_match)
            update_turn(turn)
        i = i + 1

    update_tournament(tournament)
    return


def create_next_match(turn, tournament):

    previous_turn_id = tournament.turns[-2]
    previous_turn = get_turn_from_id(previous_turn_id)
    player_1_ids = []
    player_2_ids = []
    score_players_1 = []
    score_players_2 = []

    for player_id in previous_turn.matchs:
        player_1 = (player_id[0][0])
        player_1_ids.append(player_1)
        player_2 = (player_id[1][0])
        player_2_ids.append(player_2)

        score_player_1 = player_id[0][1]
        score_players_1.append(score_player_1)
        score_player_2 = player_id[1][1]
        score_players_2.append(score_player_2)

    players_ids = player_1_ids + player_2_ids
    players_scores = score_players_1 + score_players_2
    players_elo = []

    for player_id in players_ids:
        player = get_player_from_id(player_id)
        players_elo.append(player.elo)

    info_players = []

    for i, (players_ids,
            players_elo) in enumerate(zip(players_ids, players_elo)):
        info_players.append([players_ids, players_elo])

    start_list = []

    for i, (info_players,
            players_scores) in enumerate(zip(info_players, players_scores)):
        start_list.append([info_players, players_scores])

    sorted_list = sorted(start_list, key=lambda x: (x[0], x[1]), reverse=True)
    lenght_sorted_list = len(sorted_list)
    half_length_players = int(lenght_sorted_list / 2)

    players_1 = []
    players_2 = []

    for k in range(0, half_length_players):
        first_half = sorted_list[:half_length_players]

        players_1.append(first_half[k][0])

        second_half = sorted_list[half_length_players:lenght_sorted_list]
        players_2.append(second_half[k][0])

    i = -1
    limit = int((lenght_sorted_list / 2) - 1)
    while i < limit:
        i = i + 1
        first_player_id = (players_1[i][0])

        # ------
        # test si 2 joueurs se sont d??j?? rencontr??s
        second_player_id = find_second_player(tournament, players_2)
        new_tuple_match = ([first_player_id, 0], [second_player_id, 0])
        tournament.encounters[f"{first_player_id}"] = f"{second_player_id}"
        tournament.encounters[f"{second_player_id}"] = f"{first_player_id}"
        turn.matchs.append(new_tuple_match)
    update_turn(turn)
    update_tournament(tournament)


def find_second_player(tournament, players_2):
    """Find a second player"""

    # est-ce que le player 1 a rencontre le joueur 2 qu'on va sortir
    # hasEncounter = tournament.encounters[first_player] != None
    # si hasEncounter n'est pas vide, r??cup??rer le joueur 2 suivant
    # faire une boucle sur cette partie
    index = 0
    found_player_2 = None

    while (found_player_2 is None or (index < len(players_2))):
        index += 1

        if (index >= len(players_2) - 1):
            found_player_2 = players_2.pop(0)[0]
            break

        current_player_2_list = players_2[index]
        proposed_player_2 = current_player_2_list[index]

        # PROBLEME: `encounter_player_2_id` ne devrait pas ??tre vide.
        encounter_player_2_id = tournament.encounters.get(proposed_player_2)

        if (proposed_player_2 != encounter_player_2_id):
            found_player_2 = players_2.pop(index)[0]
            break

        if (index >= len(players_2) - 1):
            proposed_player_2 = players_2.pop(index)[0]
            break
    if found_player_2 is None:
        found_player_2 = players_2.pop(0)[0]
    return found_player_2


def delete_turn(turn):
    """Delete a single turn from database."""
    db.remove(where('id') == turn.id)


def deserialize_turn(turn_data):
    """From JSON data, return a Turn instance object."""

    turn = Turn(
        turn_data['id'],
        turn_data['name'],
        turn_data['start_time'],
        turn_data['end_time'],
        turn_data['matchs'],
    )

    return turn


def save_turn(turn):
    """Save a player to the database"""

    # Generate an unique identifier for a player.
    id = uuid.uuid4().int
    db.insert(
        Document(
            {
                'id': id,
                'name': turn.name,
                'start_time': turn.start_time,
                'end_time': turn.end_time,
                'matchs': turn.matchs,
            },
            doc_id=id))
    turn.id = id
    return turn


def update_turn(turn):
    """Update a turn to the database"""
    db.update(
        {
            'id': turn.id,
            'name': turn.name,
            'start_time': turn.start_time,
            'end_time': turn.end_time,
            'matchs': turn.matchs,
        },
        doc_ids=[turn.id])

def get_all_turns():
    """Return all turns from the database as a list
       of complexe data (Dictionnary of Dictionnary)"""
    return db.all()


def get_all_turns_as_list(include_back=True):
    """Return all turns as a list of string ."""
    turns = get_all_turns()

    # Apply format_player() function to each player from database
    # and convert the result back (from an iterator) to a list.
    turns_list = list(map(format_turn, turns))

    if include_back:
        # Append 'exit' entry at the end of the list.
        turns_list.append(answers_list[Answer.BACK])

    return turns_list


def get_turn_from_id(turn_id):
    """Return a turn dictionnary from an id."""

    turn_data = db.get(doc_id=int(turn_id))

    return Turn.fromJSON(turn_data)


def format_turn(turn):
    """Format player output with name and elo."""

    turn_id = f"{turn['id']}"  # to retrieve turn data
    turn_name = f"{turn['name']} "

    return (turn_name, turn_id)


def sorte_players_by_score(tournament):
    player_score_dictionnary = {}

    player_id_list = tournament.players

    for player_id in player_id_list:
        player_score_dictionnary[player_id] = 0

    for turn_id in tournament.turns:
        turn = get_turn_from_id(turn_id)

        for match in turn.matchs:
            player_1_id = match[0][0]
            player_1_score = match[0][1]

            player_2_id = match[1][0]
            player_2_score = match[1][1]

            player_1_last_score = player_score_dictionnary[player_1_id]
            player_score_dictionnary[player_1_id] = float(
                player_1_last_score) + float(player_1_score)

            player_2_last_score = player_score_dictionnary[player_2_id]
            player_score_dictionnary[player_2_id] = float(
                player_2_last_score) + float(player_2_score)

    sorted_tuple_player_score_list = sorted(player_score_dictionnary.items(),
                                            key=lambda item: item[1],
                                            reverse=True)

    for sorted_tuple_player_score in sorted_tuple_player_score_list:
        player = get_player_from_id(sorted_tuple_player_score[0])
        score = sorted_tuple_player_score[1]


def sorte_players_by_alphabet(tournament):
    player_ids = tournament.players

    players = []
    for id in player_ids:
        player = get_player_from_id(id)
        players.append(player)
        gamers = get_all_players_as_list(players)
    players_sorted = sorted(gamers, key=lambda x: x[0])
