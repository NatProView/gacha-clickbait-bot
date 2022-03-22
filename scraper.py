from urllib.request import urlopen

url = "https://gdansk.meteo.com.pl/"


def get_temperature():
    page = urlopen(url)
    html_bytes = page.read()
    html = html_bytes.decode("utf-8")
    temp_start_index = html.find("<strong id=\"PARAM_TA\">") + len("<strong id=\"PARAM_TA\">")
    temperature = html[temp_start_index:temp_start_index + 10].partition("<")[0]
    return temperature


def get_weather():
    page = urlopen(url)
    html_bytes = page.read()
    html = html_bytes.decode("utf-8")
    temp_start_index = html.find("<strong id=\"PARAM_TA\">") + len("<strong id=\"PARAM_TA\">")
    hum_start_index = html.find("<strong id=\"PARAM_RH\">") + len("<strong id=\"PARAM_RH\">")
    pressure_start_index = html.find("<strong id=\"PARAM_PR\">") + len("<strong id=\"PARAM_PR\">")
    temperature = html[temp_start_index:temp_start_index + 10].partition("<")[0].replace(',', '.')
    humidity = html[hum_start_index:hum_start_index + 10].partition("<")[0].replace(',', '.')
    pressure = html[pressure_start_index:pressure_start_index + 10].partition("<")[0].replace(',', '.')
    if "-" in pressure:
        pressure = "N\A"

    return {"temperature": temperature,
            "humidity": humidity,
            "pressure": pressure}
