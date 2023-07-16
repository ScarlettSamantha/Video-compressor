import argparse
import logging
import os
import re
import subprocess
import time
import datetime
from threading import Thread
from tqdm import tqdm
from typing import NoReturn, Optional, Tuple

class TqdmToLogger(logging.Handler):
    """
    Log handler that sends log messages to tqdm output.
    """
    def emit(self, record):
        msg = self.format(record)
        tqdm.write(msg)

class VideoCompressor:
    """
    Class to compress a video file to a specified size using ffmpeg.
    """
    def __init__(self, input_file: str, output_file: str, max_size_mb: int, log_dir: str = "logs", additional_ffmpeg_args: Optional[str] = "", verbosity: int = 0, cpu_limit: Optional[int] = None, remove_original: bool = False) -> NoReturn:
        """
        Initialize VideoCompressor.
        """
        self.input_file = input_file
        self.output_file = output_file
        self.max_size_mb = max_size_mb
        self.log_dir = log_dir
        self.additional_ffmpeg_args = additional_ffmpeg_args
        self.verbosity = verbosity
        self.cpu_limit = cpu_limit if cpu_limit else os.cpu_count()
        self.remove_original = remove_original

        # Create log directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)

        # Set up logging
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)

        # Create file handler
        fh = logging.FileHandler(os.path.join(log_dir, 'ffmpeg.log'))
        fh.setLevel(logging.INFO)

        # Create tqdm handler
        th = TqdmToLogger()
        th.setLevel(logging.INFO)

        # Create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        th.setFormatter(formatter)

        # Add the handlers to the logger
        logger.addHandler(fh)
        if verbosity >= 2:
            logger.addHandler(th)

    def check_ffmpeg(self) -> bool:
        """
        Check if FFmpeg is installed.
        """
        try:
            subprocess.check_output("ffmpeg -version", shell=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def get_video_info(self) -> Tuple[float, int, int, int]:
        """
        Get the duration, resolution, and bit depth of the input video using ffprobe.
        """
        cmd = f"ffprobe -v error -select_streams v:0 -show_entries stream=duration,width,height,bits_per_raw_sample -of default=noprint_wrappers=1 {self.input_file}"
        output = subprocess.check_output(cmd, shell=True).decode('utf-8')

        duration_regex = re.compile(r"duration=([\d\.]+)")
        width_regex = re.compile(r"width=(\d+)")
        height_regex = re.compile(r"height=(\d+)")
        bit_depth_regex = re.compile(r"bits_per_raw_sample=(\d+)")

        duration = float(duration_regex.search(output).group(1))
        width = int(width_regex.search(output).group(1))
        height = int(height_regex.search(output).group(1))

        bit_depth_search = bit_depth_regex.search(output)
        bit_depth = int(bit_depth_search.group(1)) if bit_depth_search else 8  # use 8 as default if not found

        return duration, width, height, bit_depth

    def calculate_bitrate(self, duration: float, resolution: int, bit_depth: int) -> float:
        """
        Calculate the required bitrate for the output video.
        """
        required_file_size_bits = self.max_size_mb * 1024 * 1024 * 8
        total_pixels = duration * resolution
        bits_per_pixel = required_file_size_bits / total_pixels
        required_bitrate_kbps = (bits_per_pixel * resolution) / 1024
        return required_bitrate_kbps

    def start_compression(self) -> subprocess.Popen:
        """
        Start the ffmpeg process to compress the video.
        """
        if not self.check_ffmpeg():
            logging.error("FFmpeg is not installed. Please install FFmpeg before running this script.")
            exit(1)

        duration, width, height, bit_depth = self.get_video_info()
        resolution = width * height
        bitrate = self.calculate_bitrate(duration, resolution, bit_depth)

        cmd = f"ffmpeg -i {self.input_file} -b:v {bitrate}k -bufsize {bitrate}k -threads {self.cpu_limit} {self.additional_ffmpeg_args} {self.output_file}"
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        logging.info(f"Started compressing video from {self.input_file} to {self.output_file} with bitrate {bitrate:.2f} Mbps")

        output_thread = Thread(target=self.log_output, args=(process,))
        output_thread.start()

        return process

    def log_output(self, process: subprocess.Popen) -> NoReturn:
        """
        Log the output of the ffmpeg process.
        """
        for line in iter(process.stdout.readline, b''):
            if self.verbosity >= 3:
                logging.info(line.decode('utf-8').strip())

    def compress_video(self) -> NoReturn:
        """Compresses the video and renders/polls the toolbar.

        Returns:
            NoReturn: 
        """
        if os.path.exists(self.output_file):
            overwrite = input(f"The file {self.output_file} already exists. Do you want to overwrite it? (y/n): ")
            if overwrite.lower() != 'y':
                print("Operation cancelled.")
                return
            else:
                os.remove(self.output_file)
                start = datetime.datetime.now()
        process = self.start_compression()

        with tqdm(total=self.max_size_mb, unit='MB', ascii="░▒█") as pbar:
            while process.poll() is None:
                if os.path.exists(self.output_file):
                    output_file_size_mb = round(os.path.getsize(self.output_file) / 1024 / 1024, 4)
                    pbar.update(output_file_size_mb - pbar.n)
                time.sleep(0.25)
            pbar.update(output_file_size_mb)

        process.communicate()  # wait for the process to finish
        logging.info(f"Finished compressing video from {self.input_file} to {self.output_file} it took {round(float((datetime.datetime.now() - start).total_seconds()), 2)} Seconds")
        print(f"Finished compressing video from {self.input_file} to {self.output_file} it took {round(float((datetime.datetime.now() - start).total_seconds()), 2)} Seconds")
        if self.remove_original:
            os.remove(self.input_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", required=True)
    parser.add_argument("--output_file", required=True)
    parser.add_argument("--max_size_mb", type=int, required=True)
    parser.add_argument("--log_dir", default="logs")
    parser.add_argument("-a", "--additional_ffmpeg_args", default="")
    parser.add_argument("-v", "--verbosity", action='count', default=0)
    parser.add_argument("--cpu_limit", type=int, default=os.cpu_count())
    parser.add_argument("--remove_original", action='store_true')
    args = parser.parse_args()

    try:
        compressor = VideoCompressor(args.input_file, args.output_file, args.max_size_mb, args.log_dir, args.additional_ffmpeg_args, args.verbosity, args.cpu_limit, args.remove_original)
        compressor.compress_video()
    except KeyboardInterrupt:
        print("\nScript terminated by user. Cleaning up...")
        exit(1)