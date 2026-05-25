import json
import os
from pathlib import Path

import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

S3_BUCKET = os.environ.get("S3_BUCKET", "")
AWS_REGION = os.environ.get("AWS_REGION", "ap-south-1")


def apply_lifecycle():
    if not S3_BUCKET:
        print("ERROR: S3_BUCKET environment variable not set")
        return

    lifecycle_path = Path(__file__).parent / "lifecycle.json"
    with open(lifecycle_path) as f:
        lifecycle = json.load(f)

    s3 = boto3.client("s3", region_name=AWS_REGION)

    try:
        s3.put_bucket_lifecycle_configuration(
            Bucket=S3_BUCKET,
            LifecycleConfiguration=lifecycle,
        )
        print(f"Lifecycle policy applied to {S3_BUCKET}")

        # verify
        response = s3.get_bucket_lifecycle_configuration(Bucket=S3_BUCKET)
        for rule in response["Rules"]:
            print(f"Rule: {rule['ID']} — Status: {rule['Status']}")

    except ClientError as exc:
        print(f"ERROR: {exc}")


if __name__ == "__main__":
    apply_lifecycle()
