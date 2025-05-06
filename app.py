from flask import Flask, render_template, request, jsonify
from geopy.geocoders import Nominatim
import requests
import time
from geopy.exc import GeocoderTimedOut

app = Flask(__name__)
geolocator = Nominatim(user_agent="hangout-app")

YELP_API_KEY = "W0wSpRhfpAlI3pBrqHSpx67jGsM2h-FN9R6U60xwfuqnh_ZItjd282YT3cOHWRmQtLZHgWkdYo83vCPPKR8NEuHeqcKuPtq_FR5fWCkw5niYqgsIgvu9pqi430QFaHYx"


def geocode(address):
    retries = 3
    while retries > 0:
        try:
            location = geolocator.geocode(address, timeout=10)
            if location:
                return (location.latitude, location.longitude)
            return None
        except GeocoderTimedOut:
            retries -= 1
            time.sleep(2)  # Retry after 2 seconds
    return None


def get_average_location(locations):
    lat_sum = 0
    lon_sum = 0
    valid_locations = 0

    for loc in locations:
        coords = geocode(loc)
        if coords:
            lat_sum += coords[0]
            lon_sum += coords[1]
            valid_locations += 1

    if valid_locations == 0:
        return None

    return (lat_sum / valid_locations, lon_sum / valid_locations)


def search_yelp(category, lat, lon):
    headers = {"Authorization": f"Bearer {YELP_API_KEY}"}
    url = "https://api.yelp.com/v3/businesses/search"
    params = {
        "term": category,
        "latitude": lat,
        "longitude": lon,
        "radius": 8000,
        "limit": 5
    }
    response = requests.get(url, headers=headers, params=params)
    results = []
    if response.status_code == 200:
        data = response.json()
        for business in data.get("businesses", []):
            results.append({
                "name": business["name"],
                "address": " ".join(business["location"]["display_address"])
            })
    else:
        return {"error": "Failed to fetch data from Yelp API."}
    return results


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.get_json()

    # Check for missing or invalid data
    locations = data.get("locations", [])
    category = data.get("category", "")

    if not locations or not category:
        return jsonify({"error": "Missing locations or category"}), 400

    avg_location = get_average_location(locations)
    if not avg_location:
        return jsonify({"error": "Invalid or empty locations"}), 400

    results = search_yelp(category, avg_location[0], avg_location[1])

    if "error" in results:
        return jsonify(results), 500  # Internal server error if Yelp request fails

    return jsonify(results)


if __name__ == "__main__":
    app.run(debug=True)
