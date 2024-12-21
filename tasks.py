import pandas as pd
import boto3
from io import BytesIO
from datetime import datetime
from app import db
from models import Ambiente, AmbienteSemente, Semente
from app import create_app
from utils import list_s3_files, read_parquet_from_s3, send_mqtt_message

app = create_app()

def processar_dados_s3(bucket_name, prefix, from_date):
    try:
        df = read_parquet_from_s3(bucket_name, prefix, from_date)

        if df is None:
            return 'Nenhum arquivo encontrado para processar.'

        ambientes = []
        for _, row in df.iterrows():
            ambiente = Ambiente(
                identifier=row['identifier'],
                nodes_count=row['nodes_count'],
                temperature_mean=row['temperature_mean'],
                humidity_mean=row['humidity_mean'],
                soil_humidity_mean=row['soil_humidity_mean'],
                uv_intensity_mean=row['uv_intensity_mean'],
                soil_temperature_mean=row['soil_temperature_mean'],
                ingestion_timestamp_mean=row['ingestion_timestamp_mean'],
                light_mean=row['light_mean']
            )
            ambientes.append(ambiente)

        with app.app_context():
            db.session.bulk_save_objects(ambientes)
            db.session.commit()

        return f'{len(ambientes)} registros inseridos no banco de dados.'

    except Exception as e:
        with app.app_context():
            db.session.rollback() 
        return f'Erro ao processar os dados: {str(e)}'



# def processar_dados_s3(bucket_name, prefix, from_date):
#     try:
#         # Leitura dos arquivos do S3
#         df = read_parquet_from_s3(bucket_name, prefix, from_date)

#         if df is None or df.empty:
#             return 'Nenhum arquivo encontrado para processar.'
        
#         print(f"Arquivos lidos com sucesso: {df.shape[0]} registros encontrados.")

#         ambientes = []
#         for _, row in df.iterrows():
#             ambiente_identifier = row['identifier']

#             # Consulta o banco de dados para o ambiente
#             ambiente = Ambiente.query.filter_by(identifier=ambiente_identifier).first()
#             if ambiente is None:
#                 print(f"Ambiente {ambiente_identifier} não encontrado.")
#                 return f"Ambiente {ambiente_identifier} não encontrado no banco de dados."

#             # Consulta a relação entre ambiente e semente
#             ambiente_semente = AmbienteSemente.query.filter_by(ambiente_identifier=ambiente_identifier).first()
#             if ambiente_semente is None:
#                 print(f"Relacionamento entre ambiente {ambiente_identifier} e semente não encontrado.")
#                 return f"Relacionamento entre ambiente {ambiente_identifier} e semente não encontrado."

#             # Consulta a semente
#             semente = Semente.query.get(ambiente_semente.semente_id)
#             if semente is None:
#                 print(f"Semente com ID {ambiente_semente.semente_id} não encontrada.")
#                 return f"Semente com ID {ambiente_semente.semente_id} não encontrada."

#             # Envio da mensagem MQTT caso a umidade do solo seja menor que o mínimo
#             if row['soil_humidity_mean'] < semente.umidade_minima:
#                 print(f"Umidade do solo ({row['soil_humidity_mean']}) abaixo do mínimo para o ambiente {ambiente_identifier}. Enviando mensagem AGUAR.")
#                 send_mqtt_message(ambiente_identifier, "AGUAR", 300000)

#             # Criação do objeto ambiente
#             ambiente = Ambiente(
#                 identifier=ambiente_identifier,
#                 nodes_count=row['nodes_count'],
#                 temperature_mean=row['temperature_mean'],
#                 humidity_mean=row['humidity_mean'],
#                 soil_humidity_mean=row['soil_humidity_mean'],
#                 uv_intensity_mean=row['uv_intensity_mean'],
#                 soil_temperature_mean=row['soil_temperature_mean'],
#                 ingestion_timestamp_mean=row['ingestion_timestamp_mean']
#             )
#             ambientes.append(ambiente)

#         # Inserção no banco de dados
#         with app.app_context():
#             db.session.bulk_save_objects(ambientes)
#             db.session.commit()

#         return f'{len(ambientes)} registros inseridos no banco de dados.'

#     except Exception as e:
#         with app.app_context():
#             db.session.rollback()
#         print(f"Erro ao processar os dados: {str(e)}")  # Log completo do erro
#         return f'Erro ao processar os dados: {str(e)}'
    