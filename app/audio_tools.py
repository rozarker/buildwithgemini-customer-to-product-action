"""Multimodal audio transcription tools for Customer to Product Action agent."""

import os
from google import genai
from google.genai import types
from google.cloud import storage

PROJECT_ID = "qwiklabs-gcp-04-edadb8856cae"
BUCKET_NAME = "bwg3-qwiklabs-gcp-04-edadb8856cae"


def transcribe_audio(
    audio_source: str,
) -> str:
    """Transcribes an audio file (.mp3, .wav, .m4a) into clean text transcript using Gemini multimodal capabilities.

    Args:
        audio_source: A local file path (e.g. '/path/to/meeting.mp3') or Cloud Storage URI (e.g. 'gs://bwg3.../meeting.mp3') or filename in the public bucket.

    Returns:
        The transcribed text content of the meeting or audio recording.
    """
    client = genai.Client(
        vertexai=True,
        project=PROJECT_ID,
        location="us-central1",
    )

    # Determine file mime type
    mime_type = "audio/mp3"
    if audio_source.endswith(".wav"):
        mime_type = "audio/wav"
    elif audio_source.endswith(".m4a"):
        mime_type = "audio/m4a"

    part = None

    if audio_source.startswith("gs://"):
        part = types.Part.from_uri(file_uri=audio_source, mime_type=mime_type)
    elif os.path.exists(audio_source):
        with open(audio_source, "rb") as f:
            audio_bytes = f.read()
        part = types.Part.from_bytes(data=audio_bytes, mime_type=mime_type)
    else:
        # Check if file exists in the GCS bucket
        gcs_uri = f"gs://{BUCKET_NAME}/{audio_source}"
        part = types.Part.from_uri(file_uri=gcs_uri, mime_type=mime_type)

    prompt = (
        "Please provide a complete and accurate verbatim transcript of this audio recording. "
        "Include speaker labels if multiple speakers are present."
    )

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=[part, prompt],
    )

    return response.text or "No transcription text returned from model."
