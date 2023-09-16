from flask import Flask, request, Response
import csv
import json
from dtos import SensorLocationResponse
import logging

app = Flask(__name__)

sensor_location_data_path = "./sensors_data/SensorLocationMetadata.csv"
logging.getLogger().setLevel(logging.INFO)

@app.route('/prediction', methods=['GET'])
def getPrediction():
    args = request.args
    print(args['date'])
    return 'Prediction date {}'.format(args['date'])


@app.route('/sensor/search', methods=['GET'])
def getSensorLocation():
    name_search = request.args.get('name')
    street_search = request.args.get('street')

    with open(sensor_location_data_path, "r") as opened_file:
        sensor_location_data = csv.reader(opened_file, delimiter=";")

        for row in sensor_location_data:
            if name_search and name_search.lower() in row[5].lower() : # Name
                logging.info('Sensor name searched %s, match found %s', name_search, row[5])
                return SensorLocationResponse(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]).toJson()
            
            elif street_search and street_search.lower() in row[8].lower() : # Street
                logging.info('Sensor street searched %s, match found %s', street_search, row[8])
                return SensorLocationResponse(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]).toJson()
            
        logging.info('Sensor searched %s, no match found', name_search if name_search else street_search)
        return json.JSONEncoder().encode({})
    

