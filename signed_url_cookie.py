import base64
import datetime

import cryptography.hazmat.primitives.asymmetric.ed25519 as ed25519


from six.moves import urllib

def sign_cookie(
    url_prefix: str, key_name: str, base64_key: str, expiration_time: datetime.datetime
) -> str:

    encoded_url_prefix = base64.urlsafe_b64encode(
        url_prefix.strip().encode("utf-8")
    ).decode("utf-8")
    epoch = datetime.datetime.utcfromtimestamp(0)
    expiration_timestamp = int((expiration_time - epoch).total_seconds())
    decoded_key = base64.urlsafe_b64decode(base64_key)

    policy_pattern = (
        "URLPrefix={encoded_url_prefix}:Expires={expires}:KeyName={key_name}"
    )
    policy = policy_pattern.format(
        encoded_url_prefix=encoded_url_prefix,
        expires=expiration_timestamp,
        key_name=key_name,
    )

    digest = ed25519.Ed25519PrivateKey.from_private_bytes(decoded_key).sign(
        policy.encode("utf-8")
    )
    signature = base64.urlsafe_b64encode(digest).decode("utf-8")

    signed_policy = "Edge-Cache-Cookie={policy}:Signature={signature}".format(
        policy=policy, signature=signature
    )
    return signed_policy

# Replace with your actual values
private_key_string = "insert_base64_encoded_private_key"
url_prefix = "https://mediacdn.example.com/image-path/"
key_name = "first-keyset"
expiration = datetime.datetime.utcfromtimestamp(1800022861)  # URL valid for some time in future

print(sign_cookie(url_prefix=url_prefix, key_name=key_name, expiration_time=expiration,base64_key=private_key_string))