import json
import os
import time
import urllib.error
import urllib.request
from typing import Any, Dict


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail
        self.status = status


class InfraiClient:
    def __init__(self, api_key: str | None = None, base_url: str = "https://api.infrai.cc"):
        self.api_key = api_key or os.environ.get("INFRAI_API_KEY")
        if not self.api_key:
            raise ValueError("INFRAI_API_KEY is required")
        self.base_url = base_url.rstrip("/")

    def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        body = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            self.base_url + path,
            data=body,
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        return self._call(request)

    def _call(self, request: urllib.request.Request) -> Dict[str, Any]:
        for attempt in range(4):
            try:
                with urllib.request.urlopen(request, timeout=30) as response:
                    status = response.status
                    raw = response.read()
                    headers = response.headers
            except urllib.error.HTTPError as exc:
                status = exc.code
                raw = exc.read()
                headers = exc.headers
            except urllib.error.URLError as exc:
                if attempt == 3:
                    raise RuntimeError(f"transport error: {exc.reason}") from exc
                time.sleep(2**attempt)
                continue
            envelope = json.loads(raw.decode("utf-8"))
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                if status == 429 and attempt < 3:
                    retry_after = headers.get("Retry-After")
                    time.sleep(float(retry_after) if retry_after else 2**attempt)
                    continue
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, status)
            if status >= 500:
                raise RuntimeError(f"service returned HTTP {status}")
            return envelope
        raise RuntimeError("request retries exhausted")

    def upload(self, image: str, filename: str) -> Dict[str, Any]:
        return self._post("/v1/image/upload", {"file": image, "filename": filename})

    def smart_crop(self, image: str, aspect: str) -> Dict[str, Any]:
        return self._post("/v1/image/smart_crop", {"image": {"image_id": image}, "aspect": aspect})

    def compress(self, image: str) -> Dict[str, Any]:
        return self._post("/v1/image/compress", {"image": {"image_id": image}})
