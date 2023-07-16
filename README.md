# Video Compressor

This script compresses a video file to a specified size using FFmpeg. It calculates the required bitrate for the output file based on its duration and the target size, starts the FFmpeg process to compress the video, and displays a progress bar using tqdm.

## Usage

You can run the script with the following arguments:

- `--input_file`: The input video file. (required)
- `--output_file`: The output video file. (required)
- `--max_size_mb`: The maximum size of the output video file in MB. (required)
- `--log_dir`: The directory to write logs to. (optional, default is "logs")
- `-a` or `--additional_ffmpeg_args`: Additional FFmpeg arguments. (optional)
- `-v` or `--verbosity`: Increase output verbosity. Use `-vv` or `-vvv` for more verbosity. (optional)
- `--cpu_limit`: Limit the number of CPU cores used by FFmpeg. (optional)

### Example Commands

```bash
# Compress a video with minimal verbosity
python main.py --input_file input.mp4 --output_file output.mp4 --max_size_mb 500

# Compress a video with medium verbosity
python main.py -v --input_file input.mp4 --output_file output.mp4 --max_size_mb 500

# Compress a video with maximum verbosity
python main.py -vvv --input_file input.mp4 --output_file output.mp4 --max_size_mb 500

# Limit the number of CPU cores used by FFmpeg
python main.py --input_file input.mp4 --output_file output.mp4 --max_size_mb 500 --cpu_limit 4
```

## Installation

This script requires FFmpeg to be installed on your system.

### Ubuntu

You can install FFmpeg on Ubuntu with the following command:

```bash
sudo apt update
sudo apt install ffmpeg
```

### Fedora

On Fedora, use this command:

```bash
sudo dnf install ffmpeg
```

### macOS

On macOS, you can use Homebrew:

```bash
brew install ffmpeg
```

### Windows

On Windows, you can download FFmpeg from the [official website](https://ffmpeg.org/download.html#build-windows) and add it to your system's PATH.

## Dependencies

This script requires Python 3.6 or later and the following Python packages:

- tqdm