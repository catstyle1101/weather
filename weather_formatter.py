from weather_api_service import Weather, WindDirection


def format_weather(weather: Weather) -> str:
    """Formats weather data in string"""
    return (
        f"{weather.city}, температура {weather.temperature}°C, "
        f"{weather.weather_type}\n"
        f"Восход: {weather.sunrise.strftime('%H:%M')}\n"
        f"Закат: {weather.sunset.strftime('%H:%M')}\n"
        f"Атмосферное давление: {weather.pressure} мм.рт.ст.\n"
        f"Влажность: {weather.humidity}%\n"
        f"Ветер: {weather.wind_direction}, {weather.wind_speed} м/с"
            )


if __name__ == "__main__":
    from datetime import datetime
    from weather_api_service import WeatherType
    print(format_weather(Weather(
        temperature=25,
        weather_type=WeatherType.CLEAR,
        sunrise=datetime.fromisoformat("2022-05-03 04:00:00"),
        sunset=datetime.fromisoformat("2022-05-03 20:25:00"),
        city="Челябинск",
        pressure=750,
        humidity=70,
        wind_speed=100,
        wind_direction=WindDirection.EAST
    )))
