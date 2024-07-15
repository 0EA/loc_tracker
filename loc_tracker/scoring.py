class Normalize_and_Score_UAVData:
    def __init__(self, data, blacklisted_uav):
        self.data = data
        self.blacklisted_uav = blacklisted_uav

    def normalize(self, values):
        min_val = min(values)
        max_val = max(values)
        if min_val == max_val:
            min_val = 0
            max_val = 1
        return [(val - min_val) / (max_val - min_val) for val in values]

    def calculate_score(self, weights):
        # Extract data
        speed_values = list(self.data['speeds'].values())
        distance_values = list(self.data['distances'].values())
        angle_values = list(self.data['angles'].values())
        bearing_values = list(self.data['bearings'].values())
        height_values = list(self.data['heights'].values())
        reliability_values = list(self.data['reliability'].values())

        # Normalize data
        normalized_speeds = self.normalize(speed_values)
        normalized_distances = self.normalize(distance_values)
        normalized_angles = self.normalize(angle_values)
        normalized_bearings = self.normalize(bearing_values)
        normalized_heights = self.normalize(height_values)
        normalized_reliability = self.normalize(reliability_values)

        scores = {}
        for i, team_number in enumerate(self.data['team_numbers']):
            if team_number in self.blacklisted_uav:
                continue
            scores[team_number] = (
                weights[0] * (1 / (1 + normalized_distances[i])) +
                weights[1] * (1 / (1 + normalized_speeds[i])) +
                weights[2] * (1 / (1 + normalized_angles[i])) +
                weights[3] * (1 / (1 + normalized_bearings[i])) +
                weights[4] * (1 / (1 + normalized_heights[i])) +
                weights[5] * normalized_reliability[i]
            )
        return scores
