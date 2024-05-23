import csv

class DataExporter:
    def export_to_csv(self, data_points, filepath):
        with open(filepath, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["X", "Y"])
            for point in data_points:
                writer.writerow(point)