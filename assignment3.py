import argparse
import urllib.request
import re
import csv
from collections import Counter
from collections import defaultdict
from datetime import datetime
import logging

Image_Regex = re.compile(r".*\.(jpg|gif|png)$", re.IGNORECASE)
Browser_Regex = re.compile(r"(Firefox|Chrome|Safari|MSIE)")

def download_data(url):
    """Downloads the CSV data from the URL."""
    try:
         with urllib.request.urlopen(url) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        print(f"Error downloading file: {e}")
        return None

def process_data(csv_content):
    if not csv_content:
        print("No CSV content to process.")
        return []

    data = []
    try:
        reader = csv.reader(csv_content.splitlines())
        for row in reader:
            if len(row) <3:
                continue
            data.append({"path": row[0], "datetime": row[1], "browser": row[2]})

    except Exception as e:
        print(f"Error processing CSV data: {e}")
    return data

def image_count(data):
    """Calculates the percentage of image requests."""
    if not data:
        print("No data available to count images.")
        return

    total_requests = len(data)
    image_requests = sum(1 for entry in data if Image_Regex.match(entry["path"]))
    percent = (image_requests / total_requests) * 100 if total_requests > 0 else 0
    print(f"Image requests account for {percent:.2f}% of all requests.")

def browser_count(data):
    """Finding the most popular browser."""
    if not data:
        print("No data available to count browsers.")
        return

    browser_counts = Counter(Browser_Regex.search(entry["browser"]).group(1)
        for entry in data if Browser_Regex.search(entry["browser"]))

    if browser_counts:
        most_common = browser_counts.most_common(1)[0]
        print(f"The most popular browser is {most_common[0]} with {most_common[1]} hits.")
    else:
        print("No recognizable browser data found.")


def hourly_hits(data):
    """Counts the number of hits per hour and prints them."""
    if not data:
        logging.warning("No data available to count hourly hits.")
        return

    hour_counts = defaultdict(int)

    for entry in data:
        try:
            dt_object = datetime.strptime(entry["datetime"], "%Y-%m-%d %H:%M:%S")
            hour_counts[dt_object.hour] += 1
        except ValueError as e:
            logging.error(f"Error parsing datetime '{entry['datetime']}': {e}")
            continue

    sorted_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)

    for hour, count in sorted_hours:
        print(f"Hour {hour:02d} has {count} hits.")

def main(url):
    print(f"Running main with URL = {url}...")

    logging.info(f"Running main with URL = {url}...")
    csv_content = download_data(url)
    if csv_content is None:
        return
    data = process_data(csv_content)
    if not data:  # Check if processing failed
        return

    image_count(data)
    browser_count(data)
    hourly_hits(data)

if __name__ == "__main__":
    """Main entry point"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", help="URL to the datafile", type=str, required=True)
    args = parser.parse_args()
    main(args.url)
    
