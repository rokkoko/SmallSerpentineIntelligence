# def parseMessage(str):
#   game_name, score_pairs_str = str.split(':')
  
#   score_pairs = [score_pair_str.split() for score_pair_str in score_pairs_str.split(',')]

#   return game_name, score_pairs

message = 'Червяки: Егор 1, Саша 5, Сергей 0, Юля 3'

# print(parseMessage(message))

def parse_message(message):
  message = message.split(':')
  game_name = message[0]
  score_pairs_list = str[1].strip().split(', ')
  score_pairs = {k.split(' ')[0]: int(k.split(' ')[1]) for k in score_pairs_list}
  return game_name, score_pairs
