# Google Media CDN Signed Requests Guide

## Purpose
The purpose of this guide is to provide instructions to users who are interested in signing URL requests that are compatible with [Google Media CDN](https://cloud.google.com/media-cdn/docs/overview) in order to protect access to content they want to deliver.  The guide will cover general steps to sign individual URLs, URL Paths, URL Prefixes, and Cookies via Python.

## Pre-requisites / Assumptions
1. Read through and familiarize yourself with Access Control [documentation](https://cloud.google.com/media-cdn/docs/prevent-unauthorized-distribution-overview) for Media CDN.
2. You have a GCP project with Media CDN allow listed (written as of Jan 24')

## Step 1 - Generate required public and private keys 
Public and private keys are required in order to sign requests with Media CDN.  Asymmetric keys must be generated as Ed25519 pairs, with a 512-bit (64-byte) private key, and a 256-bit (32-byte) public key.

1. Use the following `OpenSSL` commands to generate the required private key.  **Note:** Keep this key stored in a safe place such as your own KMI or Google [Secret Manager](https://cloud.google.com/security/products/secret-manager).
   ```
   # generate an ed25519 key pair
    openssl genpkey -algorithm ed25519 -outform PEM -out sample.private.key
   ```
2. We then need to generate a public key from the private key in a URL-safe base64 format.
   ```
   # base64-encoded public key
    openssl pkey -outform DER -pubout -in sample.private.key | tail -c +13 | python3 -c "import base64, sys; print(('%s' % base64.urlsafe_b64encode(sys.stdin.buffer.read()))[2:-1])"
   ```
3. We also need to genererate a base64 version of the private key generated in step 1.  This value will be used to populate the `private_key_string` variable in the example scripts in this repo.
   ```
   # base64-encoded private key 
    openssl pkey -outform DER -in sample.private.key | tail -c +17 | python3 -c "import base64, sys; print(('%s' % base64.urlsafe_b64encode(sys.stdin.buffer.read()))[2:-1])"
   ```

## Step 2 - Create a "[keyset](https://cloud.google.com/media-cdn/docs/create-keyset)" in Media CDN
1. Within your Media CDN configuration, select the "KEYSETS" tab at the top.
2. Click "+ Create Keyset"
3. Provide a name for your keyset.  In my example, I used `first-keyset`.
   - In the code samples, you will use the keyset name in the `key_name` variable.
4. Click "Add Public Key"
5. Enter a public key ID: The ID must be 1-64 characters long, and match the regular expression [a-zA-Z][a-zA-Z0-9_-]*
   - This is a required field but is not used in any of the code samples.
7. Use the base64 public key generated in step 1.2 for the "Value"
8. Click Done
9. Click Create Keyset

**Note: These steps can also be performed via the `gcloud CLI` or Terraform.  [Find the documentation for both methods here](https://cloud.google.com/media-cdn/docs/create-keyset?hl=en#gcloud-cli).**
   
![image](https://github.com/mikehansen20/google-media-cdn-signed-requests/assets/51237503/3677afc9-862b-4520-bdc4-5dbdce994e4d)

## Step 3 - Enable Signed Requests and associate the Keyset to the Media CDN configuration
1. Assuming Media CDN has alredy been initially configured, click on the Media CDN Edge Cache Service name.
2. Click Edit
3. Click Next to navigate to "Routing"
4. Edit or Add a new route rule that you would like to enable signed requests for.
5. Expand **Advanced Configurations**
6. Under "Route action (optional), either "Add an Item" or expand an existing "CDN policy".
7. At the bottom, you will see "Signed request mode"
8. Select "REQUIRE_SIGNATURES"
9. Next, select the Keyset name you created in step 2
10. Click Done > Save > Update Service
11. It should take ~2 minutes for the update to take effect.

![image](https://github.com/mikehansen20/google-media-cdn-signed-requests/assets/51237503/7bd66d48-680f-48b8-80fc-4b0725dc6ecd)

## Step 4 - Generate signatures
It is highly recommended to reference the [Generate Signatures](https://cloud.google.com/media-cdn/docs/generate-signatures?hl=en) documentation for this next step.  

At a minimum, there are 3 required fields that must exist in each signed request: `Expires`, `KeyName`, and `Signature`.  Depending on which signing method you are using, there may be additional required fields (E.g., if you are signing a URL Prefix or using a signed cookie, the `URLPrefix` must be included as well). Optional signature fields can also be used, but that is beyond the scope of this guide. Refer to the docuemntation linked above.

## Step 5 - Using the code samples
At the bottom of each code sample, there is a section to populate the variables with values that you defined during steps 1 through 3 in this guide.  Below you will find example values to help guide you along.  

*Note: Not all of these values exist in each code sample because some are not required. Use the descriptions and values below as a guide depending on which signing method you are using.*

- `private_key_string` - This is the base64 encoded value that you generated in step 1.3.
- `original_url` - If signing individual URLs, this is the URL that you want to sign.
  - Example: `https://mediacdn.example.com/image-path/image.jpg`
- `key_name` - This is the keyset name you created in step 2.3.
  - Example: `first-keyset`
- `url_prefix` - Consists of the protocol + hostname + path to sign.
  - Example: `https://mediacdn.example.com/image-path/`
- `expiration` - The Unix/epoch timestamp to keep the signed URL valid. Some time in the future.
  - Example: `datetime.datetime.utcfromtimestamp(1800022861)`
- `filename` - The filename of the sample request.
  - Example: `image.jpg`
