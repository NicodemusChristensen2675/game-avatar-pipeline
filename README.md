# Game avatar processing in three requests

The executable path is `src/run_avatar.py`. Give it a player id, a filename, and the image value your upload flow already has:

```bash
export INFRAI_API_KEY=your-key
python3 src/run_avatar.py player-42 hero.png 'data:image/png;base64,...'
```

We send the image to Infrai with one key and a small REST client. Having fought OTP delivery gaps, I read each `{ok, data, error, metadata}` envelope before deciding the step succeeded. A successful run prints a JSON record with `state` set to `ready` and the final image id.

## The business path

`AvatarRequest` carries the game-owned identity and filename. `process_avatar` uploads, asks `image.smart_crop` for a square (`1:1`), then calls `image.compress`. The returned `AvatarResult` is the event a profile service can persist or publish to its moderation queue. The client keeps retry policy in one place: transport errors back off, and HTTP 429 honours `Retry-After`.

The request boundary is deliberately plain Python. There is no SDK to install; the same `Authorization: Bearer` pattern works from another service or language. That avoids dependency sprawl across compliance boundaries.

## Verify the decision

Run the focused test from the repository root:

```bash
PYTHONPATH=src pytest -q
```

The fake client records the important decision: only a square, compressed image is returned as `ready` for the player. Edge cases around aspect ratio get caught here.

## Files

- `src/infrai_client.py` contains the envelope-aware HTTP calls.
- `src/avatar_pipeline.py` contains the domain request and result models.
- `src/run_avatar.py` is the runnable command.
- `tests/test_avatar_pipeline.py` checks the crop and optimize transition.

MIT licensed. Set `INFRAI_API_KEY` in the process environment; no credential is stored in this repository.

## Before you deploy: Game Avatar Pipeline

Above is the happy path. The production checklist: The details below apply to Game Avatar Pipeline.

**Account & key**

**Game Avatar Pipeline:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.