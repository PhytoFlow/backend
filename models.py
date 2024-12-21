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

class Ambiente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    identifier = db.Column(db.String(10), nullable=False)
    nodes_count = db.Column(db.Integer, nullable=False)
    temperature_mean = db.Column(db.Float, nullable=False)
    humidity_mean = db.Column(db.Float, nullable=False)
    soil_humidity_mean = db.Column(db.Float, nullable=False)
    uv_intensity_mean = db.Column(db.Float, nullable=False)
    soil_temperature_mean = db.Column(db.Float, nullable=False)
    ingestion_timestamp_mean = db.Column(db.Float, nullable=False)
    light_mean = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<Ambiente {self.identifier}>"
    
    
class AmbienteSemente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    semente_id = db.Column(db.Integer, nullable=False)
    ambiente_identifier = db.Column(db.String(10), nullable=False)
    identifier = db.Column(db.String(100), nullable=False)
    
    def __repr__(self):
        return f"<AmbienteSemente {self.identifier}>"
