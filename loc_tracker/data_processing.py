from geopy.distance import geodesic as GD
from shapely.geometry import Polygon, Point
from .scoring import Normalize_and_Score_UAVData

class UAVDataProcessor:
    def __init__(self):
        self.uav_data = {}

    def update_uav_data(self, json_data):
        for data in json_data:
            team_number = data['takim_numarasi']
            if team_number not in self.uav_data:
                self.uav_data[team_number] = {
                    'latitude': [],
                    'longitude': [],
                    'altitude': [],
                    'pitch': [],
                    'bearing': [],
                    'roll': [],
                    'speed': [],
                    'time_difference': [],
                    'forbidden_status': []
                }
            for key in self.uav_data[team_number]:
                self.uav_data[team_number][key].append(data[f'iha_{key}'])

    def calculate_distances(self, our_uav_lat, our_uav_lon):
        our_uav = (our_uav_lat, our_uav_lon)
        distances = {}
        for team_number, team_data in self.uav_data.items():
            uav_coords = (team_data['latitude'][-1], team_data['longitude'][-1])
            distances[team_number] = GD(our_uav, uav_coords).km
        return distances

    def calculate_angles(self):
        angles = {}
        for team_number, team_data in self.uav_data.items():
            lat_data = team_data['latitude']
            lon_data = team_data['longitude']
            if len(lat_data) >= 3:
                angle = sum(
                    calculate_rotation_angle(
                        GD((lat_data[i-2], lon_data[i-2]), (lat_data[i-1], lon_data[i-1])).m,
                        GD((lat_data[i-1], lon_data[i-1]), (lat_data[i], lon_data[i])).m,
                        GD((lat_data[i-2], lon_data[i-2]), (lat_data[i], lon_data[i])).m
                    ) for i in range(2, len(lat_data))
                ) / (len(lat_data) - 2)
                angles[team_number] = angle
        return angles

    def calculate_bearings(self, our_uav_lat, our_uav_lon):
        bearings = {}
        for team_number, team_data in self.uav_data.items():
            bearings[team_number] = calculate_bearing(our_uav_lat, our_uav_lon, team_data['latitude'][-1], team_data['longitude'][-1])
        return bearings

    def calculate_speeds(self):
        speeds = {}
        for team_number, team_data in self.uav_data.items():
            if len(team_data['latitude']) >= 2:
                speeds[team_number] = GD(
                    (team_data['latitude'][-2], team_data['longitude'][-2]),
                    (team_data['latitude'][-1], team_data['longitude'][-1])
                ).m
            else:
                speeds[team_number] = 0
        return speeds

    def calculate_heights(self):
        return {team_number: team_data['altitude'][-1] for team_number, team_data in self.uav_data.items()}

    def coordinates_reliability(self):
        coordinates_reliability = {}
        for team_number, team_data in self.uav_data.items():
            reliability = 0
            for j in range(2, len(team_data['latitude'])):
                right_corridor_lat, right_corridor_lon = calculate_new_position(team_data['latitude'][j-2], team_data['longitude'][j-2], team_data['bearing'][j-1] + 90, -0.005)
                left_corridor_lat, left_corridor_lon = calculate_new_position(team_data['latitude'][j-2], team_data['longitude'][j-2], team_data['bearing'][j-1] - 90, -0.005)
                predicted_right_corridor_lat, predicted_right_corridor_lon = calculate_new_position(right_corridor_lat, right_corridor_lon, team_data['bearing'][j-1], -1 * (((team_data['speed'][j-1] / 1000) + 0.002)))
                predicted_left_corridor_lat, predicted_left_corridor_lon = calculate_new_position(left_corridor_lat, left_corridor_lon, team_data['bearing'][j-1], -1 * (((team_data['speed'][j-1] / 1000) + 0.002)))
                corridor_polygon = Polygon([(right_corridor_lat, right_corridor_lon), (left_corridor_lat, left_corridor_lon), (predicted_left_corridor_lat, predicted_left_corridor_lon), (predicted_right_corridor_lat, predicted_right_corridor_lon)])
                if corridor_polygon.contains(Point(team_data['latitude'][j-1], team_data['longitude'][j-1])):
                    reliability += 1
            coordinates_reliability[team_number] = reliability / (len(team_data['latitude']) - 2)
        return coordinates_reliability

    def find_best_uav(self, initial_speed, initial_altitude, our_uav_lat, our_uav_lon, our_uav_bearing, blacklisted_uav):
        distances = self.calculate_distances(our_uav_lat, our_uav_lon)
        angles = self.calculate_angles()
        bearings = self.calculate_bearings(our_uav_lat, our_uav_lon)
        speeds = self.calculate_speeds()
        heights = self.calculate_heights()
        reliability = self.coordinates_reliability()

        data = {
            'speeds': speeds,
            'distances': distances,
            'angles': angles,
            'bearings': bearings,
            'heights': heights,
            'reliability': reliability,
            'team_numbers': list(self.uav_data.keys())
        }

        weights = [0.25, 0.15, 0.20, 0.25, 0.05, 0.10]
        scoring = Normalize_and_Score_UAVData(data, blacklisted_uav)
        scores = scoring.calculate_score(weights)

        best_uav = max(scores, key=scores.get, default=None)
        if best_uav:
            print(f"Best UAV's Team Number: {best_uav}, Speed: {speeds[best_uav]} m/s, Distance: {distances[best_uav]} km, Rotation Angle: {angles[best_uav]}, Angle Between Our UAV's Bearing to Heading Best UAV: {our_uav_bearing - bearings[best_uav]}, Heights Difference: {initial_altitude - heights[best_uav]} m, Accuracy of Coordinates: {100 * reliability[best_uav]}%")
        else:
            print("There is no UAV to select")
        return best_uav

    def select_uav_data(self, best_uav):
        if best_uav:
            return (
                self.uav_data[best_uav]['latitude'],
                self.uav_data[best_uav]['longitude'],
                self.uav_data[best_uav]['altitude']
            )
        return None, None, None
