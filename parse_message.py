def parse(message):
  message = message.split(':')
  game_name = message[0]
  score_pairs_list = message[1].strip().split(', ')
  score_pairs = {k.split(' ')[0]: int(k.split(' ')[1]) for k in score_pairs_list}
  return game_name, score_pairs