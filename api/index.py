import requests
import xmltodict
from flask import jsonify
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import json

class handler(BaseHTTPRequestHandler):
    PODCAST_URL = 'https://anchor.fm/s/49f0c604/podcast/rss'
    def do_GET(self):
        # Busca e analisa os dados do podcast
        xml_text = self.fetch_podcast_data()
        podcast_data = self.parse_podcast_data(xml_text)

        # Retorna os dados do podcast em formato JSON
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(podcast_data).encode())
        return

    def rss_json(self):   
        # Busca e analisa os dados do podcast
        xml_text = self.fetch_podcast_data()
        
        if not xml_text:
            return jsonify({'error': 'Erro ao buscar o feed do podcast'})

        podcast_data = self.parse_podcast_data(xml_text)
        
        # Retorna os dados do podcast em formato JSON
        return jsonify(podcast_data)

    def fetch_podcast_data(self):
        try:
            # Fazendo a requisição para o feed RSS
            response = requests.get(self.PODCAST_URL)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar o feed RSS: {e}")
            return None

    def parse_podcast_data(self, xml_text):
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

