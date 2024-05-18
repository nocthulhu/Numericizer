import csv

class DataExporter:
    """Exports extracted data points to a CSV file."""

    def __init__(self):
        pass

    def export_to_csv(self, data_points, filepath):
        """Exports data points to a CSV file."""
        try:
            with open(filepath, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["X", "Y"])  # Header row
                for x, y in data_points:
                    writer.writerow([x, y])
            print(f"Data exported successfully to {filepath}")
        except Exception as e:
            print(f"Error exporting data: {e}")