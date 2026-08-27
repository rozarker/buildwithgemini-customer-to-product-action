"""UX Mockup image generation tool for Customer to Product Action agent."""

import uuid
from google import genai
from google.genai import types
from google.cloud import storage
from google.adk.tools import ToolContext

# Hardcoded project ID and public bucket name as explicitly required
PROJECT_ID = "qwiklabs-gcp-04-edadb8856cae"
BUCKET_NAME = "bwg3-qwiklabs-gcp-04-edadb8856cae"


def generate_ux_mockup(
    concept_description: str,
    tool_context: ToolContext,
) -> str:
    """Generates a visual UX wireframe mockup for a product opportunity concept.

    Generates the image using gemini-3.1-flash-lite-image in the global region,
    saves it to the session artifacts panel, uploads it directly to public Cloud Storage,
    and returns its public https URL.

    Args:
        concept_description: Description of the feature concept or UI mockup to visualize.
        tool_context: ADK ToolContext used to save the generated image artifact.

    Returns:
        The public HTTPS URL of the uploaded mockup image.
    """
    # Initialize Vertex AI GenAI Client in the global region
    client = genai.Client(
        vertexai=True,
        project=PROJECT_ID,
        location="global",
    )

    prompt = (
        f"A clean, modern, high-fidelity UI/UX wireframe mockup for a software application feature: "
        f"{concept_description}. Professional layout, dark mode dashboard interface, clean typography."
    )

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite-image",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
        ),
    )

    # Find generated image bytes and mime type
    image_bytes = None
    mime_type = "image/jpeg"

    if response.parts:
        for part in response.parts:
            if part.inline_data:
                image_bytes = part.inline_data.data
                mime_type = part.inline_data.mime_type or "image/jpeg"
                break

    if not image_bytes:
        return "Error: Failed to generate image bytes from model response."

    filename = f"ux_mockup_{uuid.uuid4().hex[:8]}.jpg"

    # 1. Save artifact using tool_context for the Playground Artifacts panel
    artifact_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
    tool_context.save_artifact(filename=filename, artifact=artifact_part)

    # 2. Upload image bytes directly to public Cloud Storage bucket in memory (no local disk write)
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.upload_from_string(image_bytes, content_type=mime_type)

    public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"
    return f"Generated UX Mockup Image:\n![UX Wireframe Mockup]({public_url})\nPublic GCS URL: {public_url}"
