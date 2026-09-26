from models import Bike, add_bike, find_bike


def test_bike_object_creation():
    bike = Bike(42, "Specialized Rockhopper", "Mountain")
    assert bike.id == 42
    assert bike.model == "Specialized Rockhopper"
    assert bike.type == "Mountain"
    assert bike.is_available is True


def test_bike_availability_toggle():
    bike = Bike(1, "Fixie", "Urban")
    bike.change_availability(False)
    assert bike.is_available is False


def test_add_bike_to_collection():
    collection = []
    added = add_bike(collection, 10, "Format 1411", "Cross-Country")
    assert len(collection) == 1
    assert collection[0] is added
    assert collection[0].model == "Format 1411"


def test_find_bike_by_query():
    bikes_list = [
        Bike(1, "Shulz Trekker", "Touring"),
        Bike(2, "Format 5512", "Gravel")
    ]
    results = find_bike(bikes_list, "shulz")
    assert len(results) == 1
    assert results[0].id == 1
