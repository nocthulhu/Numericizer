import csv

class DataExporter:
    def __init__(self):
        pass

    @staticmethod
    def export_to_csv(data_points, filepath):
        try:
            with open(filepath, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["X", "Y"])
                for x, y in data_points:
                    writer.writerow([x, y])
            print(f"Data exported successfully to {filepath}")
        except Exception as e:
            print(f"Error exporting data: {e}")