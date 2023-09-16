from flask import Flask, request
import csv
import json
from dtos import SensorLocationResponse, SensorTrafficData
import logging
import os

app = Flask(__name__)

logging.getLogger().setLevel(logging.INFO)

sensor_location_data_path = "./sensors_data/SensorLocationMetadata.csv"
sensor_traffic_data_path = "./data/12_06_to_24_06"

@app.route('/prediction', methods=['GET'])
def getPrediction():
    args = request.args
    print(args['date'])
    return 'Prediction date {}'.format(args['date'])

@app.route('/generate-sensor-names', methods=['GET'])
def generate_sensor_names():
    """
    Get all unique sensor names
    Example:
        http://127.0.0.1:5000/generate-sensors-names
    """
    results = set()
    with open(sensor_location_data_path, "r") as opened_file:
        sensor_location_data = csv.reader(opened_file, delimiter=";")
        for row in sensor_location_data:
            results.add(row[5])
    return {"sensor names": list(results)}

@app.route('/generate-sensor-names-streets', methods=['GET'])
def generate_sensor_names_streets():
    """
    Get all unique sensor names and streets 
    Example:
        http://127.0.0.1:5000/generate-sensor-names-streets
    """
    results = set()
    with open(sensor_location_data_path, "r") as opened_file:
        sensor_location_data = csv.reader(opened_file, delimiter=";")
        for row in sensor_location_data:
            results.add(row[5])
            results.add(row[8])
    return {"sensor names": list(results)}


@app.route('/sensor/search', methods=['GET'])
def get_sensor_location():
    """
    Get Sensor information regarding its localization
    :query params: name and street (under the tag query)
    Example:
        http://127.0.0.1:5000/sensor/search?query=enne
        http://127.0.0.1:5000/sensor/search?query=18
    """
    query_search = request.args.get('query').lower()

    if not query_search:
        return json.JSONEncoder().encode({})

    with open(sensor_location_data_path, "r") as opened_file:
        sensor_location_data = csv.reader(opened_file, delimiter=";")

        for row in sensor_location_data:
            if query_search in row[5].lower() or query_search in row[8].lower(): # Name and Street
                logging.info('Sensor searched %s, match found %s', query_search, row[5])
                return SensorLocationResponse(
                    row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]
                    ).toDictionary()
            
        logging.info('Sensor searched %s, no match found', query_search)
        return json.JSONEncoder().encode({})
    
def get_sensor_lat_and_long(sensor_id):
     with open(sensor_location_data_path, "r") as opened_file:
        sensor_location_data = csv.reader(opened_file, delimiter=";")

        for row in sensor_location_data:
            if row[0] == sensor_id:
                logging.info('Sensor id %s, latitude %s, longitude %s', row[3], row[4])
                return row[3], row[4]

    
@app.route('/historical-traffic-data/search', methods=['GET'])
def get_historical_traffic_data():
    """
    Get historical traffic information by all sensors for a specified date
    :query params: search by date in the format '2023-06-12T18:32:00.000000Z' - any substring
    Will scan through files searching for the date - after it finds one, it will scan rows and files
      until it does not find one in a row - then it stops, for efficiency
    Assumptions: 
        - Data is ordered by date
        - Each csv is a sensor
    Example:
        http://127.0.0.1:5000/historical-traffic-data/search?date=2023-06-12T18:26
    """
    date_search = request.args.get('date')
    if not date_search:
        return json.JSONEncoder().encode({})

    historical_data_files = os.listdir(sensor_traffic_data_path)
    results = list()
    
    for file in historical_data_files:
        file_path = sensor_traffic_data_path + "/" + file

        with open(file_path, "r") as opened_file:
            sensor_latitude, sensor_longitude = None, None
            sensor_traffic_data = csv.reader(opened_file, delimiter=",")

            for row in sensor_traffic_data:
                if date_search in row[2]:
                    if not sensor_latitude or not sensor_longitude:
                        sensor_latitude, sensor_longitude = get_sensor_lat_and_long(row[1])
                        
                    results.append(
                        SensorTrafficData(
                            row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], sensor_latitude, sensor_longitude
                        ).toDictionary()
                    )
                    break  # time already found
        
        if not len(results) > 0:
            break

    return { "count": len(results), "results": results }

            
        
            


    
    

