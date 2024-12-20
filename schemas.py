from marshmallow import Schema, fields

class SementeSchema(Schema):
    id = fields.Int(dump_only=True)
    nome = fields.Str(required=True)
    umidade_minima = fields.Float(required=True)
    tipo_solo = fields.Str(required=True)
    clima_necessario = fields.Str(required=True)
    temperatura_min = fields.Float(required=True)
    temperatura_max = fields.Float(required=True)
    uv = fields.Float(required=True)
