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


@app.route('/sensor/search', methods=['GET'])
def getSensorLocation():
    """
    Get Sensor information regarding its localization
    :query params: name and street
    Example:
        http://127.0.0.1:5000/sensor/search?name=enne
    """
    name_search = request.args.get('name')
    street_search = request.args.get('street')

    if not name_search and not street_search:
        return json.JSONEncoder().encode({})

    with open(sensor_location_data_path, "r") as opened_file:
        sensor_location_data = csv.reader(opened_file, delimiter=";")

        for row in sensor_location_data:
            if name_search and name_search.lower() in row[5].lower() : # Name
                logging.info('Sensor name searched %s, match found %s', name_search, row[5])
                return SensorLocationResponse(
                    row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]
                    ).toDictionary()
            
            elif street_search and street_search.lower() in row[8].lower() : # Street
                logging.info('Sensor street searched %s, match found %s', street_search, row[8])
                return SensorLocationResponse(
                    row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]
                    ).toDictionary()
            
        logging.info('Sensor searched %s, no match found', name_search if name_search else street_search)
        return json.JSONEncoder().encode({})
    
@app.route('/historical-traffic-data/search', methods=['GET'])
def getHistoricalTrafficData():
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
            sensor_traffic_data = csv.reader(opened_file, delimiter=",")

            for row in sensor_traffic_data:

                if date_search in row[2]:
                    results.append(
                        SensorTrafficData(
                            row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]
                        ).toDictionary()
                    )
                    break  # time already found
        
        if not len(results) > 0:
            break

    return { "count": len(results), "results": results }

            
        
            


    
    

