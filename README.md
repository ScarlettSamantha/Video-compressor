# Video Compressor

Video Compressor is a Python script that compresses a video to a specific size using FFmpeg. It provides a progress bar, logs the compression process, and allows for additional FFmpeg arguments to be passed.

## Requirements

- Python 3.7 or later
- FFmpeg

Python dependencies are listed in the `requirements.txt` file and can be installed with `pip`:

```bash
pip install -r requirements.txt
```

The dependencies include:

- `tqdm`: A fast, extensible progress bar for Python.

## Usage

To use Video Compressor, run the following command:

```bash
python script.py <input_file> <output_file> <max_size_mb> <log_dir> -a <additional_ffmpeg_args>
```

Where:

- `<input_file>` is the input video file.
- `<output_file>` is the output video file.
- `<max_size_mb>` is the maximum size of the output video file in MB.
- `<log_dir>` is the directory to write logs to.
- `<additional_ffmpeg_args>` (optional) are additional FFmpeg arguments.

For example:

```bash
python script.py input.mp4 output.mp4 490 logs -a "-vf 'scale=1280:-1'"
```

This command will compress `input.mp4` into `output.mp4`, aiming for a maximum size of 490 MB, write logs to the `logs` directory, and scale the video resolution to 1280x720.

Enjoy compressing your videos!