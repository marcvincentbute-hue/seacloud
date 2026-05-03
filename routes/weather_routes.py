from flask import Blueprint, jsonify
import requests
import os

weather_bp = Blueprint('weather', __name__, url_prefix='/api')

# OpenWeatherMap API Key 
WEATHER_API_KEY = "4f6afd29b8582cf75e80d86d357ce4a9" 

# Port coordinates
PORTS = {
    'Butuan Port': {'lat': 8.9475, 'lon': 125.5406},
    'Magallanes': {'lat': 9.0167, 'lon': 125.5167}
}

@weather_bp.route('/weather/<port_name>')
def get_weather(port_name):
    """Get real-time weather from OpenWeatherMap API"""
    
    if port_name not in PORTS:
        return jsonify({'error': 'Port not found'})
    
    coords = PORTS[port_name]
    
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather"
        params = {
            'lat': coords['lat'],
            'lon': coords['lon'],
            'appid': WEATHER_API_KEY,
            'units': 'metric'
        }
        
        response = requests.get(url, params=params)
        data = response.json()
        
        if response.status_code == 200:
            weather_data = {
                'port': port_name,
                'temperature': round(data['main']['temp']),
                'condition': data['weather'][0]['description'],
                'wind_speed': data['wind']['speed'],
                'humidity': data['main']['humidity'],
                'icon': data['weather'][0]['icon']
            }
            return jsonify(weather_data)
        else:
            return jsonify({'error': 'Weather API error', 'message': data.get('message', 'Unknown error')})
    
    except Exception as e:
        return jsonify({'error': 'Failed to fetch weather', 'message': str(e)})