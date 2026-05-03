from flask import Blueprint, jsonify, session, render_template
from utils.weather_checker import WeatherChecker

weather_bp = Blueprint('weather', __name__, url_prefix='/api/weather')

@weather_bp.route('/check/<port_name>')
def check_weather(port_name):
    """Check weather for a specific port"""
    return jsonify(WeatherChecker.get_weather(port_name))

@weather_bp.route('/alerts')
def get_weather_alerts():
    """Get weather alerts for all ports"""
    alerts = WeatherChecker.get_weather_alert()
    return jsonify({'alerts': alerts, 'count': len(alerts)})

@weather_bp.route('/all')
def get_all_weather():
    """Get weather for all ports"""
    all_weather = {}
    for port in WeatherChecker.PORTS:
        all_weather[port] = WeatherChecker.get_weather(port)
    return jsonify(all_weather)