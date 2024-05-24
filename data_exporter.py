import csv
import json

class DataExporter:
    def export_to_csv(self, data_points, filepath):
        with open(filepath, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["X", "Y"])
            for point in data_points:
                writer.writerow(point)

    def export_to_json(self, data_points, filepath):
        data = [{"x": point[0], "y": point[1]} for point in data_points]
        with open(filepath, 'w') as file:
            json.dump(data, file, indent=4)