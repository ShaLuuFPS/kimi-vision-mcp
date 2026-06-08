"""
Vision Bridge MCP Server — Kimi via Anthropic-compatible endpoint
Sends images through Moonshot's Anthropic Messages API, returns text.
"""
import base64
import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from anthropic import AsyncAnthropic

mcp = FastMCP("vision-bridge")

API_KEY = os.environ.get("MOONSHOT_API_KEY", "")
BASE_URL = os.environ.get("ANTHROPIC_BASE_URL", "https://api.moonshot.cn/anthropic")
MODEL = os.environ.get("VISION_MODEL", "kimi-k2.6")


def _client():
    if not API_KEY:
        return None
    return AsyncAnthropic(api_key=API_KEY, base_url=BASE_URL)


@mcp.tool()
async def describe_image(image_path: str, question: str = "") -> str:
    """
    Send an image to Kimi Vision API and get a text description.
    Use whenever you need to understand what's in an image —
    screenshots, diagrams, photos, UI, error dialogs, game visuals, etc.

    Args:
        image_path: Absolute path to the image file (PNG, JPG, GIF, WebP, BMP).
        question:   Optional specific question. If empty, returns a full description.
    """
    client = _client()
    if client is None:
        return (
            "❌ MOONSHOT_API_KEY not set.\n"
            "Add it to mcp.json env: \"MOONSHOT_API_KEY\": \"sk-your-key\"\n"
            "Get a key at: https://platform.moonshot.cn"
        )

    path = Path(image_path)
    if not path.exists():
        return f"❌ File not found: {image_path}"

    suffix = path.suffix.lower()
    media_types = {
        ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
        ".gif": "image/gif", ".webp": "image/webp", ".bmp": "image/bmp",
    }
    media_type = media_types.get(suffix)
    if media_type is None:
        return f"❌ Unsupported format: {suffix} (ok: {', '.join(media_types)})"

    try:
        with open(path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode("utf-8")
    except Exception as e:
        return f"❌ Failed to read image: {e}"

    prompt = question.strip() or (
        "请详细描述这张图片的内容。包括："
        "所有可见的文字、UI元素、布局、颜色、人物/物体、以及任何值得注意的细节。"
    )

    try:
        msg = await client.messages.create(
            model=MODEL,
            max_tokens=2048,
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data,
                        },
                    },
                    {"type": "text", "text": prompt},
                ],
            }],
        )
        # Anthropic Messages API returns content blocks
        for block in msg.content:
            if block.type == "text":
                return block.text
        return "(Kimi returned no text content)"

    except Exception as e:
        return f"❌ Kimi API error: {e}"


if __name__ == "__main__":
    mcp.run()
