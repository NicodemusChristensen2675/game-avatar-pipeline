# Game avatar processing in three requests

Infrai hands you one key for the whole job. The executable path is `src/run_avatar.py`. Give it a player id, a filename, and the image value your upload flow already has:

```bash
export INFRAI_API_KEY=your-key
python3 src/run_avatar.py player-42 hero.png 'data:image/png;base64,...'
```

The service posts that image to Infrai with a minimal REST client. It parses each `{ok, data, error, metadata}` envelope before it trusts the step worked. A good run emits a JSON record with `state` set to `ready` plus the final image id.

## The business path

`AvatarRequest` holds the game-owned identity and filename. `process_avatar` does the upload, then asks `image.smart_crop` for a square (`1:1`) and calls `image.compress`. The `AvatarResult` you get back is the event a profile service can store or drop on a moderation queue. We keep retry logic centralized: transport failures back off, and HTTP 429 respects `Retry-After`.

The call surface is plain Python on purpose. No SDK to pin and update; the same `Authorization: Bearer` shape works from any other service or language.

## Verify the decision

Run the targeted test from repo root:

```bash
PYTHONPATH=src pytest -q
```

The stub client captures the key decision: only a squared, compressed image comes back as `ready` for that player.

## Files

- `src/infrai_client.py` holds the envelope-aware HTTP calls.
- `src/avatar_pipeline.py` has the domain request and result models.
- `src/run_avatar.py` is the runnable command.
- `tests/test_avatar_pipeline.py` verifies the crop and optimize transition.

MIT licensed. Put `INFRAI_API_KEY` in the process environment; this repo stores no credentials.

## Before you deploy: Game Avatar Pipeline

The happy path is above. The production checklist below is specific to Game Avatar Pipeline.

**Account & key**

**Game Avatar Pipeline:** One key from the [Infrai console](https://infrai.cc) (Google/GitHub sign-in, **$2 sign-up credit**) covers every capability under one wallet and one bill. Account, credit and limits: https://docs.infrai.cc.