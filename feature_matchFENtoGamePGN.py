import chess
import chess.pgn
import re
import requests
import os

### constant variable ###
USER_AGENT = 'Mozlla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36'
HEADERS = {
  'User-Agent': USER_AGENT
}
### --- ###

### temporary variables ###

sample_fen_stripped = 'rq2k2r/pp1b1ppp/2nNpn2/3p4/3P4/4PN2/PP2BPPP/R1BQR1K1'
fen_plain_patern = re.compile(r'[a-zA-Z0-9]*/[a-zA-Z0-9]*/[a-zA-Z0-9]*/[a-zA-Z0-9]*/[a-zA-Z0-9]*/[a-zA-Z0-9]*/[a-zA-Z0-9]*/[a-zA-Z0-9]*')

def retrieve_game_pgn_from_chesscom(m_link: str, index_g_u: int) -> str:
  response = requests.get(m_link, headers=HEADERS)

  if response.status_code == 200:
    response_json = response.json()

  given_game_pgn = response_json['games'][index_g_u]['pgn']

  return given_game_pgn


sample_pgn = retrieve_game_pgn_from_chesscom('https://api.chess.com/pub/player/hevocity/games/2026/08', 0)

with open('sample_pgn.pgn', 'w') as f:
  f.write(sample_pgn)

sample_pgn = open('sample_pgn.pgn')

if __name__ == '__main__':
  first_game = chess.pgn.read_game(sample_pgn)

  board = first_game.board()
  for move in first_game.mainline_moves():
    board.push(move)
    candidate_fen_unstripped = board.fen()
    candidate_fen_match = fen_plain_patern.search(candidate_fen_unstripped)
    candidate_fen = candidate_fen_match.group()
    if sample_fen_stripped == candidate_fen:
      print('[Match Found!]')
      break
  sample_pgn.close()
  os.remove('sample_pgn.pgn')
  
