from app.utils.geo import build_location_key, normalize_coordinate


def test_coordinates_are_rounded_to_a_stable_precision():
    assert normalize_coordinate(-19.888912345) == -19.8889


def test_nearby_coordinates_produce_the_same_location_key():
    assert build_location_key(-19.88891, -43.80583) == build_location_key(-19.88894, -43.80581)


def test_distinct_places_produce_distinct_keys():
    assert build_location_key(-19.8889, -43.8058) != build_location_key(-23.5505, -46.6333)
