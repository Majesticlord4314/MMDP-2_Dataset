import os
import subprocess
import time
import csv
from datetime import datetime

# Define a dictionary of radio stations with their streaming URLs
radio_stations = {
    "BBC_Radio": "http://bbcmedia.ic.llnwd.net/stream/bbcmedia_radio1_mf_p",
    "NPR": "http://npr-ice.streamguys1.com/live.mp3",
    "KEXP": "http://live-aacplus-64.kexp.org/kexp64.aac"
    # Add more stations as needed
}

# Parameters for recording
duration = 60  # seconds to record per clip (adjust between 30-90 seconds as desired)
num_files = 30  # total number of audio files to collect

# Name for the dataset folder
dataset_name = "Public_Radio_Audio_Samples"
if not os.path.exists(dataset_name):
    os.mkdir(dataset_name)

# Prepare CSV file to log metadata
metadata_file = os.path.join(dataset_name, "metadata.csv")
csv_file = open(metadata_file, mode='w', newline='', encoding='utf-8')
csv_writer = csv.writer(csv_file)
csv_writer.writerow(["Station Name", "Filename", "Timestamp", "Duration (s)"])

file_count = 0

# Loop until we record the desired number of files
while file_count < num_files:
    for station_name, stream_url in radio_stations.items():
        if file_count >= num_files:
            break
        # Create a timestamped filename for each recording
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{station_name}_{timestamp}_{file_count+1}.mp3"
        output_path = os.path.join(dataset_name, filename)
        
        print(f"Recording from {station_name} for {duration} seconds...")
        # Build the ffmpeg command to capture the stream
        command = [
            "ffmpeg",
            "-y",                    # overwrite output file if exists
            "-i", stream_url,        # input stream URL
            "-t", str(duration),     # recording duration in seconds
            "-acodec", "copy",       # copy the audio codec (no re-encoding)
            output_path
        ]
        try:
            # Run ffmpeg command (stdout and stderr are captured)
            result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"Saved recording: {output_path}")
            # Log metadata for this recording
            csv_writer.writerow([station_name, filename, timestamp, duration])
            file_count += 1
        except Exception as e:
            print(f"Error recording from {station_name}: {e}")
        # Short pause between recordings (adjust as needed)
        time.sleep(2)

csv_file.close()
print("\nAudio recording process completed.")
