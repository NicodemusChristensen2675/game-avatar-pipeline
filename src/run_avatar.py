import argparse
import json

from avatar_pipeline import AvatarRequest, process_avatar
from infrai_client import InfraiClient


def main() -> None:
    parser = argparse.ArgumentParser(description="Process one game avatar")
    parser.add_argument("player_id")
    parser.add_argument("filename")
    parser.add_argument("image", help="base64 data or an upload value accepted by Infrai")
    args = parser.parse_args()
    result = process_avatar(AvatarRequest(args.player_id, args.filename, args.image), InfraiClient())
    print(json.dumps(result.__dict__, sort_keys=True))


if __name__ == "__main__":
    main()
