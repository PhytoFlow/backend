from flask import Blueprint, request, jsonify
from models import Semente
from schemas import SementeSchema 
from app import db

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/sementes', methods=['GET'])
def get_sementes():
    sementes = Semente.query.all() 
    semente_schema = SementeSchema(many=True)
    result = semente_schema.dump(sementes)
    return jsonify(result)

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
