import argparse
import logging
import os
import subprocess
import time
from threading import Thread
from tqdm import tqdm
from typing import NoReturn, Optional

class VideoCompressor:
    def __init__(self, input_file: str, output_file: str, max_size_mb: int, log_dir: str, additional_ffmpeg_args: Optional[str] = None) -> NoReturn:
        self.input_file = input_file
        self.output_file = output_file
        self.max_size_mb = max_size_mb
        self.log_dir = log_dir
        self.additional_ffmpeg_args = additional_ffmpeg_args

        # Create log directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)
        
        # Set up logging
        logging.basicConfig(filename=os.path.join(log_dir, 'ffmpeg.log'),
                            level=logging.INFO,
                            format='%(asctime)s %(message)s')
        # Add console handler
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s %(message)s')
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)

    def get_video_duration(self) -> float:
        cmd = f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {self.input_file}"
        output = subprocess.check_output(cmd, shell=True)
        return float(output)

    def calculate_bitrate(self, duration: float) -> float:
        required_file_size_bits = self.max_size_mb * 1024 * 1024 * 8
        required_bitrate_kbps = required_file_size_bits / duration / 1024
        return required_bitrate_kbps

    def start_compression(self) -> NoReturn:
        duration = self.get_video_duration()
        bitrate = self.calculate_bitrate(duration)
        
        cmd = f"ffmpeg -i {self.input_file} -b:v {bitrate}k -bufsize {bitrate}k {self.additional_ffmpeg_args} {self.output_file}"
        subprocess.Popen(cmd, shell=True)
        logging.info(f"Started compressing video from {self.input_file} to {self.output_file} with bitrate {bitrate}k")

    def track_progress(self) -> NoReturn:
        with tqdm(total=self.max_size_mb, unit='MB') as pbar:
            while not os.path.exists(self.output_file) or os.path.getsize(self.output_file) < self.max_size_mb * 1024 * 1024:
                if os.path.exists(self.output_file):
                    size_mb = os.path.getsize(self.output_file) / (1024 * 1024)
                    pbar.n = min(size_mb, self.max_size_mb)
                    pbar.refresh()
                time.sleep(0.1)
        logging.info("Compression completed.")

    def compress_video(self) -> NoReturn:
        compression_thread = Thread(target=self.start_compression)
        compression_thread.start()

        self.track_progress()

        compression_thread.join()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Compress a video to a specific size.')
    parser.add_argument('input_file', type=str, help='The input video file.')
    parser.add_argument('output_file', type=str, help='The output video file.')
    parser.add_argument('max_size_mb', type=int, help='The maximum size of the output video file in MB.')
    parser.add_argument('log_dir', type=str, help='The directory to write logs to.')
    parser.add_argument('-a', '--additional_ffmpeg_args', type=str, help='Additional FFmpeg arguments.')

    args = parser.parse_args()

    compressor = VideoCompressor(args.input_file, args.output_file, args.max_size_mb, args.log_dir, args.additional_ffmpeg_args)
    compressor.compress_video()