from geopy.distance import geodesic

# Maps location strings to coordinates
MOCK_GEOCODING = {
    'New York, NY': (40.7128, -74.0060),
    'Los Angeles, CA': (34.0522, -118.2437),
    'Chicago, IL': (41.8781, -87.6298),
    'Houston, TX': (29.7604, -95.3698),
    'Phoenix, AZ': (33.4484, -112.0740)
}

def get_user_coordinates(location_string):
    # Default to NYC if location not found
    return MOCK_GEOCODING.get(location_string, (40.7128, -74.0060))

def calculate_distances(user_lat, user_lon, facilities):
    user_coords = (user_lat, user_lon)
    for facility in facilities:
        facility_coords = (facility['lat'], facility['lon'])
        distance = geodesic(user_coords, facility_coords).miles
        facility['distance'] = round(distance, 1)
        facility['wait_time'] = get_wait_time(facility['place_id'])
    return facilities

def get_wait_time(place_id):
    try:
        conn = sqlite3.connect('quickcare.db')
        c = conn.cursor()
        c.execute("SELECT wait_time FROM wait_times WHERE place_id = ?", (place_id,))
        result = c.fetchone()
        conn.close()
        return result[0] if result else 30  # Default to 30 min
    except:
        return 30
