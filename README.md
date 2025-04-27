# Universal DDNS

A universal dynamic DNS client package for managing DNS records across various providers.

## Installation
For standard usse:
```bash
pip install universalddns
```

or for development:

```bash
pip install -e .
```

## Usage
Arguments vary per provider, but general usage follows the syntax:

```bash
universal-ddns {{ PROVIDER }} [args]
```

### Example: Cloudflare
To update your Cloudflare DNS records:

```bash
universal-ddns cloudflare --api-token YOUR_CLOUDFLARE_API_TOKEN --zone-id YOUR_CLOUDFLARE_ZONE_ID --host home.example.com --type A --ttl 60
```

## Support Providers
This list may change over time.

* Cloudflare

## Contributing
Fork the repository and create a pull request.

## License