import requests

### opens the api key file ###
with open('chessvision_api_key.env') as f:
    chessvision_api_key = f.read() 
### --- ###

with open('board.jpg', 'rb') as image:
    response = requests.post(
        'https://api.chessvision.dev/api/v1/fen',
        headers={'X-Api-Key': chessvision_api_key},
        files={'image': image},
    )
response.raise_for_status()
fen = response.json()['fen']