import requests
from datetime import datetime

class WeatherChecker:
    """Weather checker for ports"""
    
    # OpenWeatherMap API (free sign up at openweathermap.org)
    WEATHER_API_KEY = "your_openweather_api_key"  # Ilisi sa imong API key
    
    # Port locations
    PORTS = {
        'Butuan Port': {'lat': 8.9475, 'lon': 125.5299},
        'Magallanes': {'lat': 9.0167, 'lon': 125.5167},
        'Nasipit Port': {'lat': 8.9833, 'lon': 125.3333}
    }
    
    @staticmethod
    def get_weather(port_name):
        """Get current weather for a port"""
        if port_name not in WeatherChecker.PORTS:
            return {'error': 'Port not found', 'port': port_name}
        
        coords = WeatherChecker.PORTS[port_name]
        url = f"http://api.openweathermap.org/data/2.5/weather?lat={coords['lat']}&lon={coords['lon']}&appid={WeatherChecker.WEATHER_API_KEY}&units=metric"
        
        try:
            response = requests.get(url)
            data = response.json()
            
            if response.status_code == 200:
                return {
                    'port': port_name,
                    'temperature': data['main']['temp'],
                    'humidity': data['main']['humidity'],
                    'description': data['weather'][0]['description'],
                    'wind_speed': data['wind']['speed'],
                    'icon': data['weather'][0]['icon'],
                    'is_safe': WeatherChecker.is_safe(data),
                    'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            else:
                return {'error': 'Failed to fetch weather', 'port': port_name}
        except Exception as e:
            print(f"Weather error: {e}")
            return {'error': str(e), 'port': port_name}
    
    @staticmethod
    def is_safe(weather_data):
        """Check if weather is safe for travel"""
        wind_speed = weather_data.get('wind', {}).get('speed', 0)
        weather_id = weather_data.get('weather', [{}])[0].get('id', 0)
        
        # Unsafe conditions
        if wind_speed > 30:  # Wind > 30 km/h
            return False
        if weather_id >= 500:  # Rain, thunderstorm
            return False
        if weather_id >= 700:  # Fog, dust
            return False
        
        return True
    
    @staticmethod
    def get_weather_alert():
        """Get weather alert for all ports"""
        alerts = []
        for port in WeatherChecker.PORTS:
            weather = WeatherChecker.get_weather(port)
            if not weather.get('is_safe', True):
                alerts.append({
                    'port': port,
                    'condition': weather.get('description', 'Bad weather'),
                    'wind_speed': weather.get('wind_speed', 0),
                    'temperature': weather.get('temperature', 0)
                })
        return alerts