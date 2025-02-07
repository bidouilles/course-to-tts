#!/usr/bin/env python3
"""
Converts course content from a webpage into a text-to-speech (TTS) audio file.

This script retrieves content from a specified URL, extracts the main text and speaker
notes within a '<div id="content">', generates a TTS script using OpenAI, and
synthesizes the script into an MP3 audio file, also using OpenAI's TTS API.

Usage:
    python course_to_tts.py --url <COURSE_URL> [--api-key <OPENAI_API_KEY>]

Environment Variables:
    OPENAI_API_KEY: Your OpenAI API key (if not provided as a command-line argument).

Dependencies:
    - requests
    - beautifulsoup4
    - openai (>=1.0.0)
    - soundfile

Author: Your Name
Date: 2025-02-02  (Consider using dynamic date:  datetime.date.today().isoformat())
"""

import argparse
import datetime
import logging
import os
import sys
from typing import Tuple
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import warnings

# Ignore DeprecationWarning
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Configure logging
# Use a more standard format, include timestamp and module name.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)  # Use a logger instance for better control.


def extract_base_filename(url: str) -> str:
    """
    Extracts the base filename from a URL.  Prioritizes the filename
    from the URL path, falling back to a timestamp-based name if no
    filename is present in the URL.

    Args:
        url: The URL to process.

    Returns:
        The extracted or generated base filename (without extension).
    """
    parsed_url = urlparse(url)
    basename = os.path.basename(parsed_url.path)
    if basename:
        name, _ = os.path.splitext(basename)
        if name:  # Ensure we don't return an empty string if there's only an extension.
            return name
    return f"tts_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"


def fetch_div_content(url: str) -> Tuple[str, str]:
    """
    Fetches the content of the '<div id="content">' element from the given URL.
    Separates main content from speaker notes (within a <details> tag).

    Args:
        url: The URL of the webpage.

    Returns:
        A tuple containing the main content and speaker notes (as strings).

    Raises:
        requests.RequestException: If there's an error fetching the URL.
        ValueError: If the '<div id="content">' element is not found.
    """
    logger.info(f"Fetching content from URL: {url}")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
    except requests.RequestException as e:
        logger.error(f"Failed to fetch URL {url}: {e}")
        raise  # Re-raise the exception to be handled by the caller

    soup = BeautifulSoup(response.text, "html.parser")
    content_div = soup.find("div", id="content")

    if not content_div:
        logger.error(f"No <div id='content'> found in URL: {url}")
        raise ValueError("Invalid HTML content: missing <div id='content'>.")

    # Extract main content.  Prefer <main> tag, fall back to whole div.
    main_tag = content_div.find("main")
    main_content = (
        main_tag.get_text(separator="\n", strip=True)
        if main_tag
        else content_div.get_text(separator="\n", strip=True)
    )

    # Extract speaker notes from <details> tag, if present.
    speaker_notes = ""
    details_tag = content_div.find("details")
    if details_tag:
        summary_tag = details_tag.find("summary")
        notes_text = details_tag.get_text(separator="\n", strip=True)
        if summary_tag:
            summary_text = summary_tag.get_text(separator="\n", strip=True)
            speaker_notes = notes_text.replace(
                summary_text, ""
            ).strip()  # Remove summary from notes
        else:
            speaker_notes = notes_text

    logger.info("Successfully extracted main content and speaker notes.")
    return main_content, speaker_notes


def generate_tts_script(main_content: str, speaker_notes: str, api_key: str) -> str:
    """
    Generates a concise, engaging TTS script from Rust mdBook course content,
    leveraging OpenAI's API and focusing on key concepts and examples.

    Args:
        main_content: The main course content.
        speaker_notes: The speaker notes.
        api_key: The OpenAI API key.

    Returns:
        The generated TTS script.

    Raises:
        Exception: If the OpenAI API call fails.
    """
    logger.info("Generating optimized TTS script using OpenAI API...")
    client = OpenAI(api_key=api_key)

    prompt = (
        "You are a Rust programming expert tasked with converting content from a Rust course into a concise and engaging "
        "text-to-speech script.  Assume the listener is learning Rust. Focus on explaining the core Rust concepts and "
        "providing illustrative Rust code examples. The examples should be described in plain English, explaining *what* the code does, rather than presenting the raw code. "
        "Omit any meta-discussions, instructions to the presenter (like 'show what happens'), "
        "or compiler error discussions. The script should only include the text to be read aloud, "
        "without extra annotations, formatting markers, or symbols. "
        "Prioritize clarity and brevity. Extract the most important information and present it in a way that's easy to understand when spoken.\n\n"
        "Course Content (from a Rust mdBook):\n"
        f"{main_content}\n\n"
        "Speaker Notes:\n"
        f"{speaker_notes if speaker_notes else 'None'}\n\n"
        "Provide ONLY the final TTS script as plain text, suitable for direct text-to-speech conversion."
    )

    try:
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a Rust programming expert. Generate a clear, concise, and engaging TTS script for a Rust course. "
                        "Focus on key Rust concepts and examples, explaining the *behavior* of code examples in plain English. "
                        "Omit presenter instructions, error discussions, and unnecessary details. Assume the listener is a Rust learner."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            model="gpt-4o-mini",
            temperature=0.5,
            max_tokens=1000,
            top_p=0.9,
        )
        tts_script = response.choices[0].message.content.strip()
        logger.info("Optimized TTS script generated successfully.")
    except Exception as e:
        logger.error(f"OpenAI API call failed: {e}")
        raise

    return tts_script


def synthesize_audio(tts_script: str, base_filename: str, api_key: str) -> str:
    """
    Synthesizes speech from the provided TTS script using the OpenAI TTS API.

    Args:
        tts_script: The text to be synthesized.
        base_filename: The base filename for the output audio file (without extension).
        api_key:  The OpenAI API key.

    Returns:
        The filename of the generated audio file (with extension).

    Raises:
        Exception: If the OpenAI API call fails or the audio file cannot be written.

    """
    logger.info("Synthesizing audio using OpenAI TTS API...")
    client = OpenAI(api_key=api_key)
    audio_filename = f"{base_filename}.mp3"

    try:
        response = client.audio.speech.create(
            model="tts-1",  # Or "tts-1-hd" for higher quality
            voice="sage",  # Choose a voice (alloy, echo, fable, onyx, nova, shimmer)
            input=tts_script,
            response_format="mp3",  # Specify MP3 for smaller file size.
        )

        # Stream the audio to a file.  More robust than saving in memory.
        response.stream_to_file(audio_filename)
        logger.info(f"Audio file created: {audio_filename}")

    except Exception as e:
        logger.error(f"OpenAI TTS API call failed: {e}")
        raise  # Re-raise for caller to handle

    return audio_filename


def parse_arguments() -> argparse.Namespace:
    """
    Parses command-line arguments.

    Returns:
        The parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Generates a TTS script and MP3 audio file from a course URL, "
        "extracting content from the div#content element."
    )
    parser.add_argument("--url", required=True, help="The URL of the course page.")
    parser.add_argument(
        "--api-key",
        help="OpenAI API key.  Can also be provided via the OPENAI_API_KEY environment variable.",
    )
    return parser.parse_args()


def main() -> None:
    """
    Main function to orchestrate the course-to-TTS process.
    """
    logger.info("Starting course-to-TTS process...")
    args = parse_arguments()

    api_key = args.api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        logger.error(
            "OpenAI API key is required.  Provide it via --api-key or the OPENAI_API_KEY environment variable."
        )
        sys.exit(1)  # Exit with a non-zero code to indicate failure

    try:
        main_content, speaker_notes = fetch_div_content(args.url)
        tts_script = generate_tts_script(main_content, speaker_notes, api_key)
        base_filename = extract_base_filename(args.url)

        # Save the script to a text file.
        script_filename = f"{base_filename}.txt"
        with open(script_filename, "w", encoding="utf-8") as f:
            f.write(tts_script)
        logger.info(f"TTS script saved to: {script_filename}")

        audio_filename = synthesize_audio(tts_script, base_filename, api_key)
        logger.info(f"Audio file saved to: {audio_filename}")
        logger.info("Course-to-TTS process completed successfully.")

    except Exception as e:
        logger.exception(
            "An error occurred during the course-to-TTS process."
        )  # Log the full traceback
        sys.exit(1)  # Exit with error status


if __name__ == "__main__":
    main()
