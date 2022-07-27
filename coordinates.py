import json
from dataclasses import dataclass

import requests

import config
from exceptions import *


@dataclass(frozen=True)
class Coordinates:
    latitude: float
    longitude: float


def _get_ip_info():
    response = requests.get('https://ipinfo.io/json')
    if response.status_code == 200:
        return response
    else:
        raise CantGetCoordinates()


def _round_coordinates(coordinates: Coordinates) -> Coordinates:
    if not config.USE_ROUNDED_COORDS:
        return coordinates
    return Coordinates(*map(
        lambda c: round(c, 1),
        [coordinates.latitude, coordinates.longitude]
    ))


def _parse_coords():
    response = _get_ip_info()
    data = json.loads(response.text)
    try:
        coords = Coordinates(latitude=float(data['loc'].split(',')[0]), longitude=float(data['loc'].split(',')[1]))
        return coords
    except IndexError:
        raise CantGetCoordinates()


def get_coordinates():
    coords = _parse_coords()
    return _round_coordinates(coords)


if __name__ == '__main__':
    print(get_coordinates())
