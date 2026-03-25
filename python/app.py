from flask import Flask, jsonify, request
from flask_swagger_ui import get_swaggerui_blueprint
import logging
import json
import os
from flask_cors import CORS
import requests
from datetime import datetime

# Инициализация Flask приложения
app = Flask(__name__)

# Настройка Swagger UI
SWAGGER_URL = '/swagger'  # URL для доступа к документации
API_URL = 'https://raw.githubusercontent.com/dimashloyger02/super-duper-umbrella/refs/heads/main/api/swagger.json'  # Правильный путь для Flask

# Создаем blueprint для Swagger UI
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Brawl Stars API",
        'show_request_headers': True,
        'show_request_body': True
    }
)

# Регистрируем blueprint в приложении
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Добавляем маршрут для обслуживания файла swagger.json
@app.route('/swagger.json')
def serve_swagger():
    with open('swagger.json') as f:
        return jsonify(json.load(f))

# Настраиваем CORS
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:2435", 
            "https://websitedimashloyger02.vercel.app",
            "http://websitedimashloyger02.vercel.app",
            "https://brawltytlol.vercel.app",
            "http://brawltytlol.vercel.app"
        ],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# Настройка логирования
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Файл логов
file_handler = logging.FileHandler('/storage/emulated/0/python001/bot/logs/api_logs.txt')
file_handler.setLevel(logging.INFO)

# Консоль
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)

# Форматировщик
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Настройки API
USE_BRAWL_TIME = False  # Переключатель между API
API_TOKEN = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6IjhkNzViOWJlLTExYmYtNDRiYy04N2U5LWU3NGI4NmI5ZmNkZSIsImlhdCI6MTc3MjY0NTA1Niwic3ViIjoiZGV2ZWxvcGVyL2NlY2Y2MjNiLWJkMTYtZmM5Mi1kNDViLTVhZjZlMzZiZTU2MSIsInNjb3BlcyI6WyJicmF3bHN0YXJzIl0sImxpbWl0cyI6W3sidGllciI6ImRldmVsb3Blci9zaWx2ZXIiLCJ0eXBlIjoidGhyb3R0bGluZyJ9LHsiY2lkcnMiOlsiMC4wLjAuMCIsIjE0Ni4xNTguMTA1LjE1Il0sInR5cGUiOiJjbGllbnQifV19.G0RWPPkUyaqD5mXLQNI7ch6aXRALkNeQdZSILFWU-fcJDuR0Uc66XK34OiIB09GcmpC6DgzLOxMegQN8LkYKzw'  # Временно храним токен напрямую

# В Flask приложении добавьте:
@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('https://media.brawltime.ninja/avatars/28000000.webp?size=192')

# Путь к файлу данных
DATA_FILE = '/storage/emulated/0/python001/bot/user_data.json'

def load_data():
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.error(f"Ошибка при загрузке данных: {str(e)}")
        return {}

def save_data(data):
    try:
        # Создаем директорию, если её нет
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        logger.error(f"Ошибка при сохранении данных: {str(e)}")

# Получение всех пользователей
@app.route('/api/users/all', methods=['GET'])
def get_all_users():
    logger.info("Получение списка всех пользователей")
    try:
        all_users = load_data()
        if not all_users:
            return jsonify({"message": "Список пользователей пуст"}), 200
        return jsonify(list(all_users.values()))
    except Exception as e:
        logger.error(f"Ошибка при получении списка пользователей: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Получение данных конкретного пользователя
@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user_data(user_id):
    logger.info(f"Получение данных пользователя {user_id}")
    try:
        data = load_data()
        user_data = data.get(str(user_id))
        if not user_data:
            return jsonify({"error": "Пользователь не найден"}), 404
        return jsonify(user_data)
    except Exception as e:
        logger.error(f"Ошибка при получении данных пользователя {user_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Обновление данных пользователя
@app.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user_data(user_id):
    logger.info(f"Обновление данных пользователя {user_id}")
    try:
        if not request.is_json:
            return jsonify({"error": "Требуется JSON-формат"}), 400
            
        data = request.get_json()
        if not data:
            return jsonify({"error": "Пустые данные"}), 400
            
        users = load_data()
        users[str(user_id)] = {**users.get(str(user_id), {}), **data}
        save_data(users)
        return jsonify({"status": "success", "message": "Данные обновлены"}), 200
    except Exception as e:
        logger.error(f"Ошибка при обновлении данных пользователя {user_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Создание нового пользователя
@app.route('/api/users', methods=['POST'])
def create_user():
    logger.info("Создание нового пользователя")
    try:
        if not request.is_json:
            return jsonify({"error": "Требуется JSON-формат"}), 400
            
        data = request.get_json()
        
        # Проверяем наличие обязательных полей
        if not data or 'user_id' not in data:
            return jsonify({"error": "Не указан ID пользователя"}), 400
            
        user_id = data.pop('user_id')
        
        # Загружаем текущие данные
        users = load_data()
        
        # Проверяем, существует ли пользователь уже
        if str(user_id) in users:
            return jsonify({"error": "Пользователь уже существует"}), 409
            
        # Создаем нового пользователя
        users[str(user_id)] = {
            'id': user_id,
            **data
        }
        
        # Сохраняем изменения
        save_data(users)
        
        return jsonify({"status": "success", "message": "Пользователь создан", "user_id": user_id}), 201
    
    except Exception as e:
        logger.error(f"Ошибка при создании пользователя: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Удаление пользователя
@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    logger.info(f"Удаление пользователя {user_id}")
    try:
        users = load_data()
        
        if str(user_id) not in users:
            return jsonify({"error": "Пользователь не найден"}), 404
            
        # Удаляем пользователя
        del users[str(user_id)]
        save_data(users)
        
        return jsonify({"status": "success", "message": "Пользователь удален"}), 200
    
    except Exception as e:
        logger.error(f"Ошибка при удалении пользователя {user_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500
        
# Добавляем новый путь к файлу мониторинга
MONITORING_FILE = '/storage/emulated/0/python001/bot/monitoring_data.json'

def load_monitoring_data():
    try:
        if os.path.exists(MONITORING_FILE):
            with open(MONITORING_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.error(f"Ошибка при загрузке данных мониторинга: {str(e)}")
        return {}

def save_monitoring_data(data):
    try:
        os.makedirs(os.path.dirname(MONITORING_FILE), exist_ok=True)
        with open(MONITORING_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        logger.error(f"Ошибка при сохранении данных мониторинга: {str(e)}")

# Endpoint для получения данных мониторинга
@app.route('/api/monitoring', methods=['GET'])
def get_monitoring_data():
    logger.info("Получение данных мониторинга")
    try:
        monitoring_data = load_monitoring_data()
        if not monitoring_data:
            return jsonify({"message": "Данные мониторинга отсутствуют"}), 200
        return jsonify(monitoring_data)
    except Exception as e:
        logger.error(f"Ошибка при получении данных мониторинга: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Endpoint для обновления данных мониторинга
@app.route('/api/monitoring', methods=['PUT'])
def update_monitoring_data():
    logger.info("Обновление данных мониторинга")
    try:
        if not request.is_json:
            return jsonify({"error": "Требуется JSON-формат"}), 400
            
        data = request.get_json()
        if not data:
            return jsonify({"error": "Пустые данные"}), 400
            
        # Загружаем текущие данные
        current_data = load_monitoring_data()
        
        # Обновляем данные
        updated_data = {**current_data, **data}
        
        # Сохраняем изменения
        save_monitoring_data(updated_data)
        
        return jsonify({"status": "success", "message": "Данные мониторинга обновлены"}), 200
    except Exception as e:
        logger.error(f"Ошибка при обновлении данных мониторинга: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Endpoint для очистки данных мониторинга
@app.route('/api/monitoring', methods=['DELETE'])
def clear_monitoring_data():
    logger.info("Очистка данных мониторинга")
    try:
        # Очищаем файл
        save_monitoring_data({})
        return jsonify({"status": "success", "message": "Данные мониторинга очищены"}), 200
    except Exception as e:
        logger.error(f"Ошибка при очистке данных мониторинга: {str(e)}")
        return jsonify({"error": str(e)}), 500
        
def get_player_data(tag):
    if USE_BRAWL_TIME:
        return get_brawl_time_data(tag)
    else:
        return get_official_data(tag)

def get_brawl_time_data(tag):
    url = f"https://brawltime.ninja/api/player.byTag?input=%7B%22json%22%3A%22{tag}%22%7D"
    
    try:
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            if 'result' in data and 'data' in data['result']:
                return data['result']['data']['json']
            
        return None
    
    except requests.RequestException as e:
        logger.error(f"Ошибка Brawl Time API для тега {tag}: {str(e)}")
        return None

def get_official_data(tag):
    url = f"https://api.brawlstars.com/v1/players/%23{tag}"
    headers = {
        'Authorization': f'Bearer {API_TOKEN}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            logger.warning(f"Игрок с тегом {tag} не найден")
        else:
            logger.error(f"Ошибка официального API: {response.status_code} - {response.text}")
            
        return None
    
    except requests.RequestException as e:
        logger.error(f"Ошибка официального API для тега {tag}: {str(e)}")
        return None

@app.route('/api/player/<tag>', methods=['GET'])
def get_player_info(tag):
    player_data = get_player_data(tag)
    
    if not player_data:
        return jsonify({"error": "Игрок не найден или произошла ошибка"}), 404
    
    # Обработка списка бойцов
    brawlers_list = []
    for brawler in player_data.get('brawlers', []):
        brawler_info = {
            "id": brawler.get('id', 'N/A'),
            "name": brawler.get('name', 'N/A'),
            "power": brawler.get('power', 'N/A'),
            "rank": brawler.get('rank', 'N/A'),
            "trophies": brawler.get('trophies', 'N/A'),
            "highest_trophies": brawler.get('highestTrophies', 'N/A'),
            "skin": {
                "id": brawler.get('skin', {}).get('id', 'N/A'),
                "name": brawler.get('skin', {}).get('name', 'N/A')
            },
            "gadgets": [{"id": gadget.get('id', 'N/A'), "name": gadget.get('name', 'N/A')} for gadget in brawler.get('gadgets', [])],
            "star_powers": [{"id": sp.get('id', 'N/A'), "name": sp.get('name', 'N/A')} for sp in brawler.get('starPowers', [])],
            "hyper_charges": [{"id": hc.get('id', 'N/A'), "name": hc.get('name', 'N/A')} for hc in brawler.get('hyperCharges', [])]
        }
        brawlers_list.append(brawler_info)
        
            # Получаем статистику
    stats = calculate_brawler_statistics(player_data.get('brawlers', []))

# Создаем отдельную переменную для детальной статистики
    test5 = {
    "pays": {
        "total_gadgets": stats['total']['gadgets'],
        "total_star_powers": stats['total']['star_powers'],
        "total_hyper_charges": stats['total']['hyper_charges']
    }
}

    response_data = {
    "tag": tag,
    "name": player_data.get('name', 'N/A'),
    "trophies": player_data.get('trophies', 'N/A'),
    "max_trophies": player_data.get('highestTrophies', 'N/A'),
    "level": player_data.get('expLevel', 'N/A'),
    "prestige": player_data.get('totalPrestigeLevel', 'N/A'),
    "expPoints": player_data.get('expPoints', 'N/A'),
    "club": {
        "name": player_data.get('club', {}).get('name', 'N/A'),
        "tag": player_data.get('club', {}).get('tag', 'N/A')
    },
    "profileIcon": {
        "id": player_data.get('icon', {}).get('id', 'N/A'),
        "color": player_data.get('nameColor', 'N/A')
    },
    "updated": datetime.now().isoformat(),
    "victories": {
        "3vs3": player_data.get('3vs3Victories', 'N/A'),
        "solo": player_data.get('soloVictories', 'N/A'),
        "duo": player_data.get('duoVictories', 'N/A')
    },
    "brawlers": brawlers_list,
    "brawler_details": stats['details'],
    "test5": test5  # Добавляем нашу переменную
}

    return jsonify(response_data), 200
    
def calculate_brawler_statistics(brawlers_data):
    total_gadgets = 0
    total_star_powers = 0
    total_hyper_charges = 0
    
    detailed_stats = []
    
    for brawler in brawlers_data:
        gadgets_count = len(brawler.get('gadgets', []))
        star_powers_count = len(brawler.get('starPowers', []))
        hyper_charges_count = len(brawler.get('hyperCharges', []))
        
        total_gadgets += gadgets_count
        total_star_powers += star_powers_count
        total_hyper_charges += hyper_charges_count
        
        detailed_stats.append({
            "name": brawler.get('name', 'N/A'),
            "gadgets": gadgets_count,
            "star_powers": star_powers_count,
            "hyper_charges": hyper_charges_count
        })
    
    # Вывод итоговых значений после обработки всех бравлеров
    print(f"Итоговые значения:")
    print(f"Всего гаджетов: {total_gadgets}")
    print(f"Всего звездных сил: {total_star_powers}")
    print(f"Всего гиперзарядов: {total_hyper_charges}")
    
    return {
        "total": {
            "gadgets": total_gadgets,
            "star_powers": total_star_powers,
            "hyper_charges": total_hyper_charges
        },
        "details": detailed_stats
    }    

@app.errorhandler(404)
def not_found(error):
    logger.warning(f"Ресурс не найден: {request.url}")
    return jsonify({"error": "Ресурс не найден"}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Внутренняя ошибка: {str(error)}")
    return jsonify({"error": "Внутренняя ошибка сервера"}), 500

if __name__ == "__main__":
    logger.info("Запуск API сервера")
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000,
        use_reloader=False
    )
