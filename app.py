from flask import Flask, render_template, request, redirect
from geolocation import get_user_coordinates, calculate_distances
from data_fetcher import fetch_facility_data
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('quickcare.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS wait_times
                 (place_id TEXT PRIMARY KEY, wait_time INTEGER, last_updated TIMESTAMP)''')
    conn.commit()
    conn.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    init_db()
    facilities = []
    error = None
    if request.method == 'POST':
        user_location = request.form.get('location')
        if user_location:
            try:
                lat, lon = get_user_coordinates(user_location)
                all_facilities = fetch_facility_data()
                facilities = calculate_distances(lat, lon, all_facilities)
                facilities = sorted(facilities, key=lambda x: x['distance'])[:5]
            except Exception as e:
                error = f"Error processing location: {e}"
    return render_template('index.html', facilities=facilities, error=error)

@app.route('/report', methods=['POST'])
def report_wait_time():
    try:
        place_id = request.form.get('place_id')
        wait_time = int(request.form.get('wait_time'))
        conn = sqlite3.connect('quickcare.db')
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO wait_times (place_id, wait_time, last_updated) VALUES (?, ?, CURRENT_TIMESTAMP)",
                  (place_id, wait_time))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Report error: {e}")
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
