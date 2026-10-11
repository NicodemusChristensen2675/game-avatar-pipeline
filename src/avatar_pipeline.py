from dataclasses import dataclass
from typing import Any

from infrai_client import InfraiClient


@dataclass(frozen=True)
class AvatarRequest:
    player_id: str
    filename: str
    image: str
    aspect: str = "1:1"


@dataclass(frozen=True)
class AvatarResult:
    player_id: str
    image_id: str
    state: str


def process_avatar(request: AvatarRequest, client: InfraiClient) -> AvatarResult:
    uploaded = client.upload(request.image, request.filename)
    upload_data: Any = uploaded["data"]
    image_id = upload_data.get("image_id") or upload_data.get("id") or upload_data.get("image")
    cropped = client.smart_crop(image_id, request.aspect)
    cropped_id = cropped["data"].get("image_id") or cropped["data"].get("id") or cropped["data"].get("image")
    optimized = client.compress(cropped_id)
    final_id = optimized["data"].get("image_id") or optimized["data"].get("id") or optimized["data"].get("image")
    return AvatarResult(request.player_id, final_id, "ready")
