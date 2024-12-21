from collections import defaultdict
from datetime import datetime, timedelta, timezone
import logging
import math
import random  # Alteração: Usando o módulo de logging do Python
from flask import Blueprint, request, jsonify
from sqlalchemy import create_engine
from models import Ambiente, Semente
from schemas import SementeSchema
from app import db
from utils import read_parquet_from_s3, send_mqtt_message

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__, url_prefix='/api')

# Rota para obter sementes
@api_bp.route('/sementes', methods=['GET'])
def get_sementes():
    sementes = Semente.query.all() 
    semente_schema = SementeSchema(many=True)
    result = semente_schema.dump(sementes)
    return jsonify(result)

# Rota para criar sementes
@api_bp.route('/sementes', methods=['POST'])
def create_semente():
    data = request.get_json()

    if not data or not all(key in data for key in ['nome', 'umidade_minima', 'tipo_solo', 'clima_necessario', 'temperatura_min', 'temperatura_max', 'uv']):
        return jsonify({'message': 'Dados insuficientes para criar a semente'}), 400

    semente = Semente(
        nome=data['nome'],
        umidade_minima=data['umidade_minima'],
        tipo_solo=data['tipo_solo'],
        clima_necessario=data['clima_necessario'],
        temperatura_min=data['temperatura_min'],
        temperatura_max=data['temperatura_max'],
        uv=data['uv']
    )

    db.session.add(semente)
    db.session.commit()

    return jsonify({
        'message': 'Semente criada com sucesso!',
        'semente': {
            'id': semente.id,
            'nome': semente.nome,
            'umidade_minima': semente.umidade_minima,
            'tipo_solo': semente.tipo_solo,
            'clima_necessario': semente.clima_necessario,
            'temperatura_min': semente.temperatura_min,
            'temperatura_max': semente.temperatura_max,
            'uv': semente.uv
        }
    }), 201

# Rota para carregar dados do S3
@api_bp.route('/load_data', methods=['GET'])
def load_data():
    df = read_parquet_from_s3('iot-data-rk76', 'aggregated', datetime.now(timezone.utc) - timedelta(days=2))

    if df is None:
        return jsonify({'message': 'No data found in S3 bucket'}), 404

    engine = create_engine('postgresql+psycopg2://jair:123@localhost:5432/pythoflow_producao')

    try:
        df.to_sql('your_table_name', engine, index=False, if_exists='append')
        return jsonify({'message': 'Data loaded successfully!'}), 200
    except Exception as e:
        return jsonify({'message': f'Error loading data: {str(e)}'}), 500

# Rota para enviar comando "AGUAR"
@api_bp.route('/aguar', methods=['POST'])
def aguar_command():
    """Recebe um comando e o envia para o broker MQTT."""
    try:
        data = request.get_json()
        identifier = data.get('identifier')
        time_duration = data.get('time')
        command = "AGUAR"

        if not identifier or not time_duration:
            return jsonify({'message': 'Parâmetros "identifier" e "time" são obrigatórios.'}), 400

        send_mqtt_message(identifier, command, time_duration)
        return jsonify({'message': 'Comando AGUAR enviado com sucesso!'}), 200

    except Exception as e:
        logger.error(f"Erro ao processar a requisição: {e}")
        return jsonify({'message': f'Erro interno: {str(e)}'}), 500


@api_bp.route('/sensors', methods=['GET'])
def get_sensors():
    identifier = request.args.get('identifier')
    
    if identifier:
        sensores = Ambiente.query.filter(Ambiente.identifier == identifier).all()
        if not sensores:
            return jsonify({"message": f"No sensors found with identifier {identifier}"}), 404
    else:
        sensores = Ambiente.query.all()

    result = []
    for sensor in sensores:
        sensor_data = {
            "identifier": sensor.identifier,
            "name": f"Sensor {sensor.identifier}",
            "working": True,
            "irrigationAvailable": True,
            "coordinate": {
                "latitude":  -16.60337,
                "longitude": -49.26625
            },
            "values": {
                "temperature": sensor.temperature_mean,
                "humidity": sensor.humidity_mean,
                "soil_humidity": sensor.soil_humidity_mean,
                "light": 500.0,
                "uv_intensity": sensor.uv_intensity_mean,
                "soil_temperature": sensor.soil_temperature_mean
            }
        }
        result.append(sensor_data)
    
    return jsonify(result) if result else jsonify([])


@api_bp.route('/current', methods=['GET'])
def current():
    sensores = Ambiente.query.all()

    # Cria um dicionário para agrupar sensores por identificador
    grouped_sensores = defaultdict(list)

    for sensor in sensores:
        grouped_sensores[sensor.identifier].append(sensor)

    result = []
    
    for identifier, sensors in grouped_sensores.items():
        # Define working como True apenas para os identificadores A1, A2 e B1
        is_working = identifier in ["A1", "A2", "B1"]
        

        sensor_data = {
            "identifier": identifier,
            "name": f"Sensor {identifier}",
            "working": is_working,
            "irrigationAvailable": True,
            "coordinate": {
                "latitude": -16.60337,
                "longitude": -49.26625
            },
            "values": []
        }
        
        if identifier == "A1":
            sensor_data["coordinates"] = {"latitude": -16.60289, "longitude": -49.26536}
                
        elif identifier == "A2":
            sensor_data["coordinates"] = {"latitude": -16.60088433458758, "longitude": -49.26570230991262 } 
        
        # Para cada sensor com o mesmo identificador, cria um objeto dentro de "values"
        for sensor in sensors:
            sensor_data["values"].append({
                "temperature": round(sensor.temperature_mean, 2),
                "humidity": round(sensor.humidity_mean, 2),
                "soil_humidity": round(sensor.soil_humidity_mean, 2),
                "light": round(500.0, 2),  # Este valor parece ser fixo, mas aplicamos o round para garantir a consistência
                "uv_intensity": round(sensor.uv_intensity_mean, 2),
                "soil_temperature": round(sensor.soil_temperature_mean, 2)
            })
        
        result.append(sensor_data)

    return jsonify(result) if result else jsonify([])

@api_bp.route('/dashboard', methods=['GET'])
def get_dashboard():
    sensores = Ambiente.query.all()

    if sensores:
        # Agrupar sensores pelo identificador
        grouped_sensores = defaultdict(list)
        for sensor in sensores:
            grouped_sensores[sensor.identifier].append(sensor)

        result = []

        # Para cada grupo de sensores agrupados pelo identificador
        for identifier, sensors in grouped_sensores.items():
            sensor_data = {
                "identifier": identifier,
                "name": f"Sensor {identifier}",
                "values": []
            }

            # Adiciona as coordenadas ao 'identifier' A1
            if identifier == "A1":
                sensor_data["coordinates"] = {"latitude": -16.60289, "longitude": -49.26536}
                
            elif identifier == "A2":
                sensor_data["coordinates"] = {"latitude": -16.60088433458758, "longitude": -49.26570230991262 } 
            

            # Para cada sensor dentro do mesmo identificador, cria um objeto dentro de "values"
            for sensor in sensors:
                sensor_data["values"].append({
                    "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
                    "temperature": round(sensor.temperature_mean, 2) if sensor.temperature_mean is not None and not math.isnan(sensor.temperature_mean) else 0,
                    "humidity": round(sensor.humidity_mean, 2) if sensor.humidity_mean is not None and not math.isnan(sensor.humidity_mean) else 0,
                    "soil_humidity": round(sensor.soil_humidity_mean, 2) if sensor.soil_humidity_mean is not None and not math.isnan(sensor.soil_humidity_mean) else 0,
                    "light": round(sensor.light_mean if sensor.light_mean is not None and not math.isnan(sensor.light_mean) else 0, 2),  
                    "uv_intensity": round(sensor.uv_intensity_mean, 2) if sensor.uv_intensity_mean is not None and not math.isnan(sensor.uv_intensity_mean) else 0,
                    "soil_temperature": round(sensor.soil_temperature_mean, 2) if sensor.soil_temperature_mean is not None and not math.isnan(sensor.soil_temperature_mean) else 0
                })
            
            result.append(sensor_data)

        return jsonify(result)
    else:
        return jsonify([])
