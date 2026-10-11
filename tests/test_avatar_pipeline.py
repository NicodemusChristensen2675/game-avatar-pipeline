from avatar_pipeline import AvatarRequest, process_avatar
from infrai_client import InfraiClient


class FakeClient:
    def upload(self, image, filename):
        assert filename.endswith(".png")
        return {"ok": True, "data": {"image_id": "raw-avatar"}}

    def smart_crop(self, image, aspect):
        assert image == "raw-avatar"
        assert aspect == "1:1"
        return {"ok": True, "data": {"image_id": "cropped-avatar"}}

    def compress(self, image):
        assert image == "cropped-avatar"
        return {"ok": True, "data": {"image_id": "ready-avatar"}}


def test_avatar_becomes_ready_after_crop_and_compress():
    result = process_avatar(AvatarRequest("p-42", "hero.png", "data:image"), FakeClient())
    assert result.player_id == "p-42"
    assert result.image_id == "ready-avatar"
    assert result.state == "ready"


def test_image_references_use_image_id_objects():
    client = InfraiClient(api_key="test-key")
    calls = []
    client._post = lambda path, payload: calls.append((path, payload))

    client.smart_crop("raw-avatar", "1:1")
    client.compress("cropped-avatar")

    assert calls == [
        ("/v1/image/smart_crop", {"image": {"image_id": "raw-avatar"}, "aspect": "1:1"}),
        ("/v1/image/compress", {"image": {"image_id": "cropped-avatar"}}),
    ]
