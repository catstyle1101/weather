import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from json import JSONDecodeError
from typing import Literal, Union, Optional
from urllib.error import URLError

import requests

import config
from exceptions import ApiServiceError
from coordinates import Coordinates

Celsius = float
millimeters_of_mercury = int


class WeatherType(str, Enum):
    THUNDERSTORM = "Гроза"
    DRIZZLE = "Изморось"
    RAIN = "Дождь"
    SNOW = "Снег"
    CLEAR = "Ясно"
    FOG = "Туман"
    CLOUDS = "Облачно"


class WindDirection(str, Enum):
    EAST = 'Восточный'
    WEST = 'Западный'
    SOUTH = 'Южный'
    NORTH = 'Северный'
    NORTHEAST = 'Северо-восточный'
    NORTHWEST = 'Северо-западный'
    SOUTHEAST = 'Юго-Восточный'
    SOUTHWEST = 'Юго-западный'


@dataclass(frozen=True)
class Weather:
    temperature: Celsius
    weather_type: WeatherType
    sunrise: datetime
    sunset: datetime
    city: str
    pressure: millimeters_of_mercury
    humidity: int
    wind_speed: Optional[int]
    wind_direction: Optional[WindDirection]


def get_weather(coordinates: Coordinates) -> Weather:
    response = _get_openweather_response(
        longitude=coordinates.longitude, latitude=coordinates.latitude)
    weather = _parse_openweather_response(response)
    return weather


def _get_openweather_response(latitude: float, longitude: float) -> str:
    url = config.OPENWEATHER_URL.format(
        latitude=latitude, longitude=longitude)
    try:
        return requests.get(url).text
    except URLError:
        raise ApiServiceError


def _parse_pressure(openweather_dict):
    try:
        return int(openweather_dict["main"]["pressure"] * 0.750063755419211)
    except KeyError:
        raise ApiServiceError


def _parse_humidity(openweather_dict):
    try:
        return openweather_dict["main"]["humidity"]
    except KeyError:
        raise ApiServiceError


def _parse_wind_speed(openweather_dict):
    try:
        return openweather_dict["wind"]["speed"]
    except KeyError:
        raise ApiServiceError


def _parse_wind_direction(openweather_dict):
    try:
        deg = float(openweather_dict["wind"]["deg"])
    except KeyError:
        raise ApiServiceError
    directions = ((WindDirection.NORTH, (337.5, 22.5)), (WindDirection.NORTHEAST, (22.5, 67.5)),
                  (WindDirection.EAST, (67.5, 112.5)), (WindDirection.SOUTHEAST, (112.5, 157.5)),
                  (WindDirection.SOUTH, (157.5, 202.5)), (WindDirection.SOUTHWEST, (202.5, 247.5)),
                  (WindDirection.WEST, (247.5, 292.5)), (WindDirection.NORTHWEST, (292.5, 337.5)))
    for direction, degree in directions:
        if degree[0] <= deg % 360 < degree[1]:
            return direction
        if deg >= 337.5 or deg < 22.5:
            return direction


def _parse_openweather_response(openweather_response: str) -> Weather:
    try:
        openweather_dict = json.loads(openweather_response)
    except JSONDecodeError:
        raise ApiServiceError
    return Weather(
        temperature=_parse_temperature(openweather_dict),
        weather_type=_parse_weather_type(openweather_dict),
        sunrise=_parse_sun_time(openweather_dict, "sunrise"),
        sunset=_parse_sun_time(openweather_dict, "sunset"),
        city=_parse_city(openweather_dict),
        pressure=_parse_pressure(openweather_dict),
        humidity=_parse_humidity(openweather_dict),
        wind_speed=_parse_wind_speed(openweather_dict),
        wind_direction=_parse_wind_direction(openweather_dict)
    )


def _parse_temperature(openweather_dict: dict) -> Celsius:
    return round(openweather_dict["main"]["temp"])


def _parse_weather_type(openweather_dict: dict) -> WeatherType:
    try:
        weather_type_id = str(openweather_dict["weather"][0]["id"])
    except (IndexError, KeyError):
        raise ApiServiceError
    weather_types = {
        "1": WeatherType.THUNDERSTORM,
        "3": WeatherType.DRIZZLE,
        "5": WeatherType.RAIN,
        "6": WeatherType.SNOW,
        "7": WeatherType.FOG,
        "800": WeatherType.CLEAR,
        "80": WeatherType.CLOUDS
    }
    for _id, _weather_type in weather_types.items():
        if weather_type_id.startswith(_id):
            return _weather_type
    raise ApiServiceError


def _parse_sun_time(
        openweather_dict: dict,
        time: Union[Literal["sunrise"], Literal["sunset"]]) -> datetime:
    return datetime.fromtimestamp(openweather_dict["sys"][time])


def _parse_city(openweather_dict: dict) -> str:
    try:
        return openweather_dict["name"]
    except KeyError:
        raise ApiServiceError


if __name__ == "__main__":
    print(get_weather(Coordinates(latitude=55.154, longitude=61.4291)))
