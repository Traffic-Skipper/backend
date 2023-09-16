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

    def toJson(self):
        return json.JSONEncoder().encode(
            {
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
        ) 


