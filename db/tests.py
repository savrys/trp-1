import unittest

from db.init_db import initialize_database
from db.import_json import import_json_data
from db.repository import (
    get_all_bikes,
    get_available_bikes,
    get_bike_by_id,
    get_all_rentals,
    get_active_rentals,
    get_bike_counts_by_type,
    get_rental_counts_by_user,
)


class DatabaseTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        initialize_database()
        import_json_data()

    def test_get_all_bikes(self):
        bikes = get_all_bikes()
        self.assertEqual(len(bikes), 3)

    def test_get_available_bikes(self):
        bikes = get_available_bikes()
        self.assertEqual(len(bikes), 2)

    def test_get_bike_by_id(self):
        bike = get_bike_by_id(3)
        self.assertIsNotNone(bike)
        self.assertEqual(bike["id"], 3)

    def test_get_missing_bike(self):
        bike = get_bike_by_id(999)
        self.assertIsNone(bike)

    def test_get_all_rentals(self):
        rentals = get_all_rentals()
        self.assertEqual(len(rentals), 1)

    def test_get_active_rentals(self):
        rentals = get_active_rentals()
        self.assertEqual(len(rentals), 1)

    def test_get_bike_counts_by_type(self):
        counts = get_bike_counts_by_type()
        self.assertGreater(len(counts), 0)

    def test_get_rental_counts_by_user(self):
        counts = get_rental_counts_by_user()
        self.assertEqual(len(counts), 2)


if __name__ == "__main__":
    unittest.main()