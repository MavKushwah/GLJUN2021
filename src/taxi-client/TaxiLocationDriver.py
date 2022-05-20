import json

from TaxiModels import TaxiLocationPublisher, TaxiLocationContext, RandomLocationGenerator, Taxi_Status, Taxi
from TaxiController import Taxi_Controller
import random

topic_arn = "arn:aws:sns:us-east-1:466703995071:topic-taxi-location"
taxi_location_dict = {}
taxi_location_publisher = TaxiLocationPublisher(topic_arn)
boundary = [-73.856077, 40.848447, -74.856077, 41.848447]
incrementBy: float = 0.00001


def name_generator():
    first_name = ["manjunath", "Dinesh", "Harish", "Divakar", "Alex", "Forex"]
    second_name = ["Godda", "Thiruappa", "Sinha", "Sharma", "Mazumder", "Mukherjee"]
    return f'{random.choice(first_name)} {random.choice(second_name)}'


taxi_controller = Taxi_Controller()
taxi_array = taxi_controller.register_mock_taxi(7)  # This is needs to separated from this file.

while True:
    for taxi in taxi_array:
        taxi_context: TaxiLocationContext = taxi_location_dict.get(taxi.id)

        if taxi_context is None:
            random_location_generator = RandomLocationGenerator(boundary, incrementBy)
            taxi: Taxi = taxi
            taxi_status: Taxi_Status = Taxi_Status(taxi_id=taxi.id,
                                                   location=random_location_generator.getNextLocation(),
                                                   state=None,
                                                   riding_with=None)
            taxi_location_dict[id] = TaxiLocationContext(taxi, random_location_generator,
                                                                               taxi_status)
        else:
            random_location_generator = taxi_context.get_location_generator()
            taxi = taxi_context.get_taxi()
            taxi.location = random_location_generator.getNextLocation()
        print(f"{taxi}", taxi.__str__())
        taxi_status_json = {"id": taxi.id,
                            "location": taxi.location,
                            "last_updated_time": json.dumps(taxi.last_updated_time, default=str)
                            }
        taxi_location_publisher.publish(taxi_status_json)


