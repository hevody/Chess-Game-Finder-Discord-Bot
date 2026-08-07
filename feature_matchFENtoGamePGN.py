import chess
import chess.pgn
import re
import requests
import os

### config ###
DEBUG = True
### --- ###

### function variable ###
monthly_list = []

# I need to do everything locally (as in, in this computer) so that it would be fast
# remove a lot of online API calls (requests) i.e we need a caching system

### constant variable ###
USER_AGENT = 'Mozlla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36'
HEADERS = {
  'User-Agent': USER_AGENT
}
fen_plain_patern = re.compile(r'[a-zA-Z0-9]*/[a-zA-Z0-9]*/[a-zA-Z0-9]*/[a-zA-Z0-9]*/[a-zA-Z0-9]*/[a-zA-Z0-9]*/[a-zA-Z0-9]*/[a-zA-Z0-9]*')
### --- ###

### temporary variables ###
given_fen_user = '2rqk2r/p2bbppp/1pn5/2pnp3/8/1Q1PBNP1/PP2PPBP/2R2RK1 w k - 0 13'
given_fen_user = '2B5/8/5k2/6pp/8/5K1P/8/8 b - - 3 49'
TimeControl = 600

def validate_game_pgn_to_fen(index_g_u: int, given_fen: str) -> bool: # will return if the game was found or not
  try:
    candidate_pgn_var = monthly_list[index_g_u]['pgn']
  except KeyboardInterrupt:
    exit()
  except:
    return False

  
  with open('candidate.pgn', 'w', encoding='utf-8') as f:
    f.write(candidate_pgn_var)

  candidate_pgn_var = open('candidate.pgn')

  possible_game = chess.pgn.read_game(candidate_pgn_var)

  this_game_time_control = possible_game.headers['TimeControl']

  if not this_game_time_control == str(TimeControl):
    candidate_pgn_var.close()
    os.remove('candidate.pgn')
    return False

  board = possible_game.board()
  for move in possible_game.mainline_moves():
    board.push(move)
    candidate_fen_unstripped = board.fen()
    candidate_fen_match = fen_plain_patern.search(candidate_fen_unstripped)
    candidate_fen = candidate_fen_match.group()
    if given_fen == candidate_fen:
      if DEBUG == True:
        print('[Match Found!]')
      candidate_pgn_var.close()
      os.remove('candidate.pgn')
      return True
  candidate_pgn_var.close()
  os.remove('candidate.pgn')
  return False
  
def get_game_archive(g_a_url) -> list:
  if DEBUG == True:
      print('[INSIDE] retrieve_game_archive_from_chesscom')
  while True:
    response = requests.get(g_a_url, headers=HEADERS)

    if response.status_code == 200:
      response_json = response.json()
      return response_json['archives']
    else:
      if response.json()['code'] == 0:
        return []
      continue

def cache_monthly_json(m_link: str) -> list:
  while True:
    response = requests.get(m_link, headers=HEADERS)
    
    if response.status_code == 200:
      response_json = response.json()
      return response_json['games']
    else:
      continue

def matchfen_to_link(cc_username: str, given_fen_unstripped: str, depth_of_month: int) -> str:
  global monthly_list
  ### strip given_fen ###
  given_fen_match = fen_plain_patern.search(given_fen_unstripped)
  given_fen = given_fen_match.group()

  # challenge: username and given fen to game link
  game_archive = get_game_archive(f'https://api.chess.com/pub/player/{cc_username}/games/archives')
  if game_archive == []:
    return '[This user does not exist]'
  game_archive.reverse()  

  game_archive_depth_of_month = []
  for game_archive_month_index in range(depth_of_month):
    game_archive_depth_of_month += [game_archive[game_archive_month_index]]

  for month_link in game_archive_depth_of_month:
    monthly_list = cache_monthly_json(m_link=month_link)
    for game_index in range(len(monthly_list)):
      if DEBUG == True:
        print(game_index)
      game_found = validate_game_pgn_to_fen(game_index, given_fen=given_fen)
      if game_found:
        game_link = monthly_list[game_index]['url']
        return game_link
  return "[GAME NOT FOUND]"

if __name__ == '__main__':
  print(matchfen_to_link(cc_username='Lorenz_Julien_Tee', given_fen_unstripped=given_fen_user, depth_of_month=1))
  
