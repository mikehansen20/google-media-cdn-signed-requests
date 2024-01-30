import base64
import datetime
import time
import cryptography.hazmat.primitives.asymmetric.ed25519 as ed25519


from six.moves import urllib

def sign_url(
    url: str, key_name: str, base64_key: str, expiration_time: datetime.datetime
) -> str:

    stripped_url = url.strip()
    parsed_url = urllib.parse.urlsplit(stripped_url)
    query_params = urllib.parse.parse_qs(parsed_url.query, keep_blank_values=True)
    epoch = datetime.datetime.utcfromtimestamp(0)
    expiration_timestamp = int((expiration_time - epoch).total_seconds())
    decoded_key = base64.urlsafe_b64decode(base64_key)

    url_pattern = "{url}{separator}Expires={expires}&KeyName={key_name}"

    url_to_sign = url_pattern.format(
        url=stripped_url,
        separator="&" if query_params else "?",
        expires=expiration_timestamp,
        key_name=key_name,
    )

    digest = ed25519.Ed25519PrivateKey.from_private_bytes(decoded_key).sign(
        url_to_sign.encode("utf-8")
    )
    signature = base64.urlsafe_b64encode(digest).decode("utf-8")
    signed_url = "{url}&Signature={signature}".format(
        url=url_to_sign, signature=signature
    )

    return signed_url

# Replace with your actual values
private_key_string = "insert_base64_encoded_private_key" 
key_name = "first-keyset"
original_url = "https://mediacdn.example.com/image-path/image.jpg"
expiration = datetime.datetime.utcfromtimestamp(1800022861)  # URL valid for some time in future

print(sign_url(url=original_url, key_name=key_name, expiration_time=expiration,base64_key=private_key_string))
