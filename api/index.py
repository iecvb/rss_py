import requests
import xmltodict
from flask import Flask, request, jsonify

PODCAST_URL = 'https://anchor.fm/s/49f0c604/podcast/rss'

app = Flask(__name__)

@app.route('/rss', methods=['GET'])
def rss_json():
    """HTTP Cloud Function.
    Args:
        request (flask.Request): The request object.
        <https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data>
    Returns:
        The response text, or any set of values that can be turned into a
        Response object using `make_response`
        <https://flask.palletsprojects.com/en/1.1.x/api/#flask.make_response>.
    """
    # Permite requisições de qualquer origem
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET',
        'Access-Control-Allow-Headers': 'Content-Type',
    }

    if request.method == 'OPTIONS':
        # Handle preflight requests
        return ('', 204, headers)

    # Busca e analisa os dados do podcast
    xml_text = fetch_podcast_data()
    
    if not xml_text:
        return jsonify({'error': 'Erro ao buscar o feed do podcast'}), 500, headers

    podcast_data = parse_podcast_data(xml_text)
    
    # Retorna os dados do podcast em formato JSON
    return jsonify(podcast_data), 200, headers

def fetch_podcast_data():
    try:
        # Fazendo a requisição para o feed RSS
        response = requests.get(PODCAST_URL)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Erro ao buscar o feed RSS: {e}")
        return None

def parse_podcast_data(xml_text):
    # Converte o XML em um dicionário usando xmltodict
    podcast_dict = xmltodict.parse(xml_text)
    items = podcast_dict['rss']['channel']['item']

    podcast_data = []
    for item in items:
        title = item['title']
        enclosure_url = item['enclosure']['@url']
        image_url = item.get('itunes:image', {}).get('@href', 'Imagem indisponível')

        podcast_data.append({
            'name': title,                        
            'url': enclosure_url,
            'cover_art_url': image_url
        })

    return podcast_data[:20]

if __name__ == '__main__':
    app.run()