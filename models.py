from app import db

class Semente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    umidade_minima = db.Column(db.Float, nullable=False)
    tipo_solo = db.Column(db.String(100), nullable=False)
    clima_necessario = db.Column(db.String(100), nullable=False)
    temperatura_min = db.Column(db.Float, nullable=False)
    temperatura_max = db.Column(db.Float, nullable=False)
    uv = db.Column(db.Float, nullable=False)
