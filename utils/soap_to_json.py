import requests
import xmltodict
from datetime import datetime
from typing import List
import json


ROAD_API_KEY="eyJvcmciOiI2NDA2NTFhNTIyZmEwNTAwMDEyOWJiZTEiLCJpZCI6IjZhYTk3NmZkMWU1MDRjZmI5MmQ5ODY5ZmQ4ZWI5ZmRmIiwiaCI6Im11cm11cjEyOCJ9"


class MeasurementIndexMapperService:
    def __init__(self):
        self._indexMap = {}
        with open('utils/assets/measurementIndexMap.json', 'r') as file:
            self._indexMap = json.load(file)

    def get_vehicle(self, id):
        if id in self._indexMap:
            return self._indexMap[id]['vehicle']
        else:
            return ''

    def get_unit(self, id):
        if id in self._indexMap:
            return self._indexMap[id]['unit']
        else:
            return ''


class AstraApiService:
    def __init__(self):
        self._auth = '57c5dbbbf1fe4d0001000018e4f31816e24e419094fb6fbcafb7be42'
        self._url = 'http://localhost:4200/api'
        self._body = self.get_body_from_file('utils/assets/SoapRequestBody.xml')
        self.index_mapper = MeasurementIndexMapperService()

    def get_body_from_file(self, file_path):
        with open(file_path, 'r') as file:
            body = file.read()
        return body

    def fetch_data_from_url(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            raise Exception(f"Error: Unable to fetch data. Status code: {response.status_code}")

    def map_to_measurement(self, raw: str, index_mapper, data_value):
        xml_dict = xmltodict.parse(raw, process_namespaces=True, namespaces={"xmlns": None})
        print(xml_dict.keys())
        payload_publication = xml_dict['Envelope']['Body']['d2LogicalModel']['payloadPublication']
        publication_time = datetime.strptime(payload_publication['publicationTime']['#text'], "%Y-%m-%dT%H:%M:%S.%fZ")
        site_measurements = payload_publication['siteMeasurements']['measurementSiteMeasurements']

        measurements = []

        for site_measurement in site_measurements:
            site_id = site_measurement['measurementSiteReference']['@_id']
            measured_values = site_measurement['measuredValue']

            measurement_data = []
            if isinstance(measured_values, list):
                for measured_value in measured_values:
                    data = measured_value['measuredValue']['basicData']
                    vehicle = index_mapper.get_vehicle(measured_value['@_index'])
                    unit = index_mapper.get_unit(measured_value['@_index'])
                    value = data_value(data)
                    measurement_data.append({'vehicle': vehicle, 'unit': unit, 'value': value})
            else:
                measured_value = measured_values['measuredValue']['basicData']
                vehicle = index_mapper.get_vehicle(measured_values['@_index'])
                unit = index_mapper.get_unit(measured_values['@_index'])
                value = data_value(measured_value)
                measurement_data.append({'vehicle': vehicle, 'unit': unit, 'value': value})

            measurements.append({'site_id': site_id, 'timestamp': publication_time, 'data': measurement_data})

        return measurements

    def get_static_measurements(self):
        raw_data = self.get_body_from_file('utils/assets/StaticMeasurements.xml')
        measurements = self.map_to_measurement(raw_data, self.index_mapper, self.get_measurement_data_value)
        return measurements

    def get_measurements(self):
        body = self.get_body_from_file('utils/assets/SoapRequestBody.xml')
        headers = {
            'Content-Type': 'text/plain',
            'Authorization': self._auth,
            'SOAPAction': 'http://opentransportdata.swiss/TDP/Soap_Datex2/Pull/v1/pullMeasuredData'
        }
        response = requests.post(self._url, data=body, headers=headers)
        raw_data = response.text
        measurements = self.map_to_measurement(raw_data, self.index_mapper, self.get_measurement_data_value)
        return measurements

    def get_measurement_data_value(self, basic_data):
        if 'averageVehicleSpeed' in basic_data and 'speed' in basic_data['averageVehicleSpeed']:
            return float(basic_data['averageVehicleSpeed']['speed']['#text'])
        elif 'vehicleFlow' in basic_data:
            return float(basic_data['vehicleFlow']['vehicleFlowRate']['#text'])
        else:
            return 0.0

    def get_lanes(self):
        body = self.get_body_from_file('assets/SoapRequestBody.xml')
        headers = {
            'Content-Type': 'text/plain',
            'Authorization': self._auth,
            'SOAPAction': 'http://opentransportdata.swiss/TDP/Soap_Datex2/Pull/v1/pullMeasurementSiteTable'
        }
        response = requests.post(self._url, data=body, headers=headers)
        raw_data = response.text
        lanes = self._map_to_lanes(raw_data)
        return lanes

    def get_static_lanes(self):
        raw_data = self.fetch_data_from_url('assets/StaticMeasurementSites.xml')
        lanes = self._map_to_lanes(raw_data)
        return lanes

    def _map_to_lanes(self, raw_data):
        xml_dict = xmltodict.parse(raw_data, process_namespaces=True, namespaces={"xmlns": None})
        measurement_site_records = xml_dict['Envelope']['Body']['d2LogicalModel']['payloadPublication']['measurementSiteTable']['measurementSiteRecord']

        lanes = []

        for site in measurement_site_records:
            site_id = site['@_id']
            location = site['measurementSiteLocation']['alertCPoint']['alertCMethod4PrimaryPointLocation']['alertCLocation']['specificLocation']['#text']
            longitude = site['measurementSiteLocation']['pointByCoordinates']['pointCoordinates']['longitude']['#text']
            latitude = site['measurementSiteLocation']['pointByCoordinates']['pointCoordinates']['latitude']['#text']
            lanes.append({'site_id': site_id, 'location': location, 'latitude': float(latitude), 'longitude': float(longitude)})

        return lanes