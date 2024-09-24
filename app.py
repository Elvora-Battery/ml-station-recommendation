from flask import Flask, request, render_template, jsonify
from collections import OrderedDict
import requests
import math

app = Flask(__name__)

# Fungsi untuk mendapatkan data stasiun dari Open Charge Map
def get_stations():
    url = "https://api.openchargemap.io/v3/poi/"
    params = {
        'output': 'json',
        'countrycode': 'ID',  # Ganti dengan kode negara yang sesuai
        'maxresults': 100,
        'key': '96bcfd74-5ad5-4095-9d39-60f0e2d977bc'  # Tambahkan API Key di sini
    }
    response = requests.get(url, params=params)
    
    # Periksa apakah respons berhasil
    if response.status_code != 200:
        raise Exception(f"API request failed with status code {response.status_code}")

    try:
        return response.json()
    except requests.exceptions.JSONDecodeError:
        print(f"Failed to parse JSON: {response.text}")
        raise

# Fungsi untuk menghitung jarak menggunakan rumus Haversine
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Radius bumi dalam kilometer
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance

# Route untuk mendapatkan rekomendasi stasiun terdekat
@app.route('/recommendations', methods=['POST'])
def get_recommendations():
    user_location = request.json['location']
    stations = get_stations()  # Ambil data stasiun dari API

    recommendations = []

    # Hitung jarak dari lokasi pengguna ke setiap stasiun
    for station in stations:
        station_lat = station['AddressInfo']['Latitude']
        station_lon = station['AddressInfo']['Longitude']
        distance = haversine(user_location['latitude'], user_location['longitude'], station_lat, station_lon)

        recommendations.append({
            'station': station['AddressInfo']['Title'],
            'distance': distance,
            'latitude' :station['AddressInfo']['Latitude'],
            'longitude': station['AddressInfo']['Longitude']
        })

    # Pilih tiga stasiun terdekat berdasarkan jarak
    recommendations = sorted(recommendations, key=lambda x: x['distance'])[:3]

    return jsonify({'stations': recommendations})

if __name__ == '__main__':
    app.run(debug=True)
