import base64
import datetime
import hashlib
import hmac

import cryptography.hazmat.primitives.asymmetric.ed25519 as ed25519


def base64_encoder(value: bytes) -> str:

    encoded_bytes = base64.urlsafe_b64encode(value)
    encoded_str = encoded_bytes.decode("utf-8")
    return encoded_str.rstrip("=")


def sign_path_component(
    url_prefix: str,
    filename: str,
    key_name: str,
    base64_key: str,
    expiration_time: datetime.datetime,
) -> str:

    expiration_duration = expiration_time.astimezone(
        tz=datetime.timezone.utc
    ) - datetime.datetime.fromtimestamp(0, tz=datetime.timezone.utc)
    decoded_key = base64.urlsafe_b64decode(base64_key)

    policy_pattern = "{url_prefix}edge-cache-token=Expires={expires}&KeyName={key_name}"
    policy = policy_pattern.format(
        url_prefix=url_prefix,
        expires=int(expiration_duration.total_seconds()),
        key_name=key_name,
    )

    digest = ed25519.Ed25519PrivateKey.from_private_bytes(decoded_key).sign(
        policy.encode("utf-8")
    )
    signature = base64_encoder(digest)

    signed_url = "{policy}&Signature={signature}/{filename}".format(
        policy=policy, signature=signature, filename=filename
    )

    return signed_url

# Replace with your actual values
private_key_string = "insert_base64_encoded_private_key"
url_prefix = "https://mediacdn.example.com/image-path/"
key_name = "first-keyset"
filename = "sample.jpg"
expiration = datetime.datetime.utcfromtimestamp(1800022861)  # URL valid for some time in future

print(sign_path_component(url_prefix=url_prefix, filename=filename, key_name=key_name, expiration_time=expiration,base64_key=private_key_string))