# Course-to-TTS

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

Convert course webpages into spoken audio using OpenAI's TTS API. This script fetches content from a specified URL, intelligently extracts the main text and speaker notes, generates a clean text-to-speech script, and synthesizes it into an MP3 audio file.

## Features

*   **Webpage Content Extraction:**  Fetches and parses HTML content, specifically targeting the `<div id="content">` element, making it adaptable to many course websites.
*   **Smart Content Separation:** Distinguishes between main course content and speaker notes (within `<details>` tags), allowing for focused TTS generation.
*   **OpenAI Integration:** Leverages OpenAI's powerful chat completion and TTS models for high-quality script generation and audio synthesis.
*   **Streaming Audio Synthesis:** Uses OpenAI's streaming API to handle large audio files efficiently, preventing memory issues.
*   **Automatic Filenaming:** Generates output filenames based on the URL, keeping your files organized.
*   **Error Handling:** Includes robust error handling and logging for a smooth user experience.
*   **Command-Line Interface:** Easy-to-use command-line interface with clear arguments.

## Prerequisites

*   Python 3.8 or higher
*   An OpenAI API key

## Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/<your-username>/course-to-tts.git
    cd course-to-tts
    ```

2.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

    (Create a `requirements.txt` file containing the following):

    ```
    requests
    beautifulsoup4
    openai>=1.0.0
    soundfile
    ```

## Usage

```bash
python course_to_tts.py --url <COURSE_URL> [--api-key <OPENAI_API_KEY>]
```

*   **`--url <COURSE_URL>`:**  (Required) The URL of the course page you want to convert.
*   **`--api-key <OPENAI_API_KEY>`:** (Optional) Your OpenAI API key.  If not provided here, you must set the `OPENAI_API_KEY` environment variable.

**Example:**

```bash
python course_to_tts.py --url https://linfo2315.pelsser.eu/course-1/what-is-rust --api-key sk-your-openai-api-key
```

Alternatively, set the environment variable:

```bash
export OPENAI_API_KEY=sk-your-openai-api-key
python course_to_tts.py --url https://linfo2315.pelsser.eu/course-1/what-is-rust
```

**Sample Output:**

```
2025-02-07 11:25:10 - __main__ - INFO - Starting course-to-TTS process...
2025-02-07 11:25:10 - __main__ - INFO - Fetching content from URL: https://linfo2315.pelsser.eu/course-1/what-is-rust
2025-02-07 11:25:11 - __main__ - INFO - Successfully extracted main content and speaker notes.
2025-02-07 11:25:11 - __main__ - INFO - Generating TTS script using OpenAI API...
2025-02-07 11:25:18 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/chat/completions "HTTP/1.1 200 OK"
2025-02-07 11:25:18 - __main__ - INFO - TTS script generated successfully.
2025-02-07 11:25:18 - __main__ - INFO - TTS script saved to: what-is-rust.txt
2025-02-07 11:25:18 - __main__ - INFO - Synthesizing audio using OpenAI TTS API...
2025-02-07 11:25:19 - httpx - INFO - HTTP Request: POST https://api.openai.com/v1/audio/speech "HTTP/1.1 200 OK"
2025-02-07 11:25:33 - __main__ - INFO - Audio file created: what-is-rust.mp3
2025-02-07 11:25:33 - __main__ - INFO - Audio file saved to: what-is-rust.mp3
2025-02-07 11:25:33 - __main__ - INFO - Course-to-TTS process completed successfully.
```

The script will create two files in the same directory:

*   `what-is-rust.txt`: The generated text-to-speech script.
*   `what-is-rust.mp3`: The synthesized audio file.

## Environment Variables

*   **`OPENAI_API_KEY`:**  Your OpenAI API key.  This is required if you don't provide the `--api-key` argument.

## Troubleshooting

*   **`No <div id='content'> found` error:** The script couldn't find the main content container on the webpage.  This script is designed to work with webpages that structure their main content within a `<div>` tag with the ID "content".  It may not work with all websites.
*   **`OpenAI API key is required` error:**  You need to provide your OpenAI API key either through the `--api-key` argument or by setting the `OPENAI_API_KEY` environment variable.
*   **`Failed to fetch URL` error:**  Check your internet connection and ensure the URL is valid and accessible.
*   **`OpenAI API call failed` error:**  This could be due to various reasons, including network issues, incorrect API key, or exceeding your OpenAI API usage limits. Check the error message for more details.

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.