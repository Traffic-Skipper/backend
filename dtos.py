import json

class SensorLocationResponse:
    def __init__(self, id, lane, orientation, lat, lon, name, canton, direction, street):
        self.id = id
        self.lane = lane
        self.orientation = orientation
        self.latitude = lat
        self.longitude = lon
        self.name = name
        self.canton = canton
        self.direction = direction
        self.street = street

    def toDictionary(self):
        return {
                "id": self.id,
                "lane": self.lane,
                "orientation": self.orientation,
                "latitude": self.latitude,
                "longitude": self.longitude,
                "name": self.name,
                "canton": self.canton,
                "direction": self.direction,
                "street": self.street
             }
    

class SensorTrafficData:
    def __init__(self, record_id, sensor_id, timestamp, car_flow, lorry_flow, any_flow, car_speed, lorry_speed, any_speed):
        self.record_id = record_id
        self.sensor_id = sensor_id
        self.timestamp = timestamp
        self.car_flow = car_flow
        self.lorry_flow = lorry_flow
        self.any_flow = any_flow
        self.car_speed = car_speed
        self.lorry_speed = lorry_speed
        self.any_speed = any_speed

    def toDictionary(self):
        return {
                "record_id": self.record_id,
                "sensor_id": self.sensor_id,
                "timestamp": self.timestamp,
                "car_flow": self.car_flow,
                "lorry_flow": self.lorry_flow,
                "any_flow": self.any_flow,
                "car_speed": self.car_speed,
                "lorry_speed": self.lorry_speed,
                "any_speed": self.any_speed
            }

