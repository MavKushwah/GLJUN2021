import json
from datetime import datetime

from TaxiModels import Taxi, RandomLocationGenerator
import requests
import random

boundary = [-73.856077, 40.848447, -74.856077, 41.848447]
incrementBy: float = 0.00001
taxi_registration_url = "https://vz76retedl.execute-api.us-east-1.amazonaws.com/v1"
taxi_type = ["Utility", "Deluxe", "Luxury"]


class Taxi_Controller:
    def __init__(self):
        self.registration_url = taxi_registration_url
        self.taxi_array = []

    def __register(self, taxi: Taxi):
        header = {"Content-type": "application/json",
                  "Accept": "*/*"}
        taxi_json = {"id": taxi.id,
                     "driver_name": taxi.driver_name,
                     "type": taxi.type,
                     "location": taxi.location,
                     "vehicle_number": taxi.vehicle_number,
                     "last_updated_time": json.dumps(taxi.last_updated_time, default=str)
                     }
        response = requests.post(self.registration_url, data=json.dumps(taxi_json), headers=header)
        print(response)
        return json.loads(response.json()["response"])['_id']

    def register_mock_taxi(self, count):
        for i in range(1, count + 1):
            id = 'Taxi-{counter}'.format(counter=i)

            random_location_generator = RandomLocationGenerator(boundary, incrementBy)
            taxi: Taxi = Taxi(id,
                              self.__name_generator(),
                              self.__taxi_type_generator(),
                              self.__vehicle_number_generator(),
                              random_location_generator.getNextLocation(),
                              datetime.now())
            taxi._id = self.__register(taxi)
            print(f"{taxi}", taxi.__str__())
            self.taxi_array.append(taxi)
        return self.taxi_array

    def __name_generator(self):
        first_name = ["Manjunath", "Dinesh", "Harish", "Divakar", "Alex", "Forex"]
        second_name = ["Godda", "Thiruappa", "Sinha", "Sharma", "Mazumder", "Mukherjee"]
        return f'{random.choice(first_name)} {random.choice(second_name)}'

    def __taxi_type_generator(self):
        return random.choice(taxi_type)

    def __vehicle_number_generator(self):
        var1 = random.randint(1200, 9999)
        var2 = random.randint(10, 99)
        return f"KA/{var1}/{var2}"
