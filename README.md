
# Universal DDNS

A universal dynamic DNS client package for managing DNS records across various providers.

## Installation

```bash
pip install universalddns
```

or for development:

```bash
pip install -e .
```

## Usage
To update your Cloudflare DNS records:

```bash
universal-ddns cloudflare --api-token YOUR_CLOUDFLARE_API_TOKEN --zone-id YOUR_CLOUDFLARE_ZONE_ID --host home.example.com --type A --ttl 60
```

## Supported Providers
* Cloudflare