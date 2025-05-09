import logging
import argparse
import os
from universalddns.models.providers.cloudflare import CloudflareDDNSClient
from universalddns.base_client import DNSRecord

def main():
    parser = argparse.ArgumentParser(
        description="Universal Dynamic DNS Updater")
    parser.add_argument(
        "provider", help="The DNS provider to use (e.g., cloudflare)")
    parser.add_argument(
        "--api-token", help="The API token for the DNS provider")
    parser.add_argument(
        "--zone-id", help="The Zone ID for the DNS provider (if applicable)")
    parser.add_argument(
        "--host",
        action='append',
        default=[],
        help="The hostnames to update (e.g., home.example.com)")
    parser.add_argument(
        "--type",
        action='append',
        default=[],
        help="The record type (e.g., A)")
    parser.add_argument(
        "--ttl",
        action='append',
        default=[],
        type=int,
        help="The TTL for the records")

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s')

    if not args.provider:
        logging.error("Error: Please specify a provider.")
        return

    if not args.host or not args.type or not args.ttl:
        logging.error("Error: Please specify at least one host, type, and TTL.")
        return

    if len(args.host) != len(args.type) or len(args.host) != len(args.ttl):
        logging.error("Error: The number of hosts, types, and TTLs must match.")
        return

    dns_records_to_update = []
    for i in range(len(args.host)):
        dns_records_to_update.append(
            DNSRecord(host=args.host[i], type=args.type[i], data="", ttl=args.ttl[i])
        )

    if args.provider.lower() == "cloudflare":
        if not args.api_token or not args.zone_id:
            logging.error(
                "Error: For Cloudflare, --api-token and --zone-id are required.")
            return
        client = CloudflareDDNSClient(
            api_token=args.api_token, zone_id=args.zone_id)
        try:
            client.update_records(dns_records_to_update)
            logging.info("Cloudflare DNS update process completed.")
        except Exception as e:
            logging.error(f"Error during Cloudflare update: {e}")
    else:
        logging.error(f"Error: Provider '{args.provider}' is not currently supported.")

if __name__ == "__main__":
    main()