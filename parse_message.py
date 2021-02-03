def parse_message(message):
    """
    :param message: from IFTTT
    :return: tuple of 2 element: [0] game_name(str) and [1] score_pairs(dict)
    """

    if ':' not in message:
        return message
    message = message.split(':')
    game_name = message[0]
    score_pairs_list = message[1].strip().split(', ')
    score_pairs = \
        {k.split(' ')[0]: int(k.split(' ')[1]) for k in score_pairs_list}
    return game_name, score_pairs
