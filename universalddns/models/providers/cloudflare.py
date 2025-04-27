# universalddns/models/providers/cloudflare.py
import httpx
from typing import List, Dict
from universalddns.base_client import BaseDDNSClient, DNSRecord

class CloudflareRecord(DNSRecord):
    """
    Represents a Cloudflare DNS record.
    """
    def __init__(self, host: str, type: str, data: str, ttl: int, record_id: str = None, proxied: bool = False):
        super().__init__(host, type, data, ttl)
        self.record_id = record_id
        self.proxied = proxied

class CloudflareDDNSClient(BaseDDNSClient):
    """
    A Dynamic DNS client for Cloudflare.
    """
    def __init__(self, api_token: str, zone_id: str):
        self.api_token = api_token
        self.zone_id = zone_id
        self.api_url = f"https://api.cloudflare.com/client/v4/zones/{self.zone_id}/dns_records"
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }

    def _get_public_ip(self) -> str:
        """
        Gets the current public IP address using ipconfig.io.
        """
        try:
            response = httpx.get("https://ipconfig.io/ip", timeout=5)
            response.raise_for_status()
            return response.text.strip()
        except httpx.RequestError as e:
            raise Exception(f"Failed to connect to get public IP: {e}")
        except httpx.HTTPStatusError as e:
            raise Exception(f"Failed to get public IP (status {e.response.status_code}): {e.response.text}")

    def _get_existing_records(self) -> List[CloudflareRecord]:
        """
        Retrieves all DNS records for the zone from Cloudflare.
        """
        try:
            response = httpx.get(self.api_url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            if data.get("success") and data.get("result"):
                records = []
                for record in data["result"]:
                    records.append(
                        CloudflareRecord(
                            host=record["name"],
                            type=record["type"],
                            data=record["content"],
                            ttl=record["ttl"],
                            record_id=record["id"],
                            proxied=record.get("proxied", False)
                        )
                    )
                return records
            else:
                raise Exception(f"Failed to get Cloudflare records: {data.get('errors')}")
        except httpx.RequestError as e:
            raise Exception(f"Failed to connect to Cloudflare API: {e}")
        except httpx.HTTPStatusError as e:
            raise Exception(f"Failed to get Cloudflare records (status {e.response.status_code}): {e.response.text}")

    def _update_record(self, record: CloudflareRecord, new_ip: str):
        """
        Updates an existing DNS record on Cloudflare.
        """
        payload = {
            "type": record.type,
            "name": record.host,
            "content": new_ip,
            "ttl": record.ttl,
            "proxied": record.proxied
        }
        try:
            url = f"{self.api_url}/{record.record_id}"
            response = httpx.put(url, headers=self.headers, json=payload)
            response.raise_for_status()
            data = response.json()
            if not data.get("success"):
                raise Exception(f"Failed to update record {record.host}: {data.get('errors')}")
            print(f"Updated record: {record.host} to {new_ip}")
        except httpx.RequestError as e:
            raise Exception(f"Failed to connect to Cloudflare API to update {record.host}: {e}")
        except httpx.HTTPStatusError as e:
            raise Exception(f"Failed to update record {record.host} (status {e.response.status_code}): {e.response.text}")

    def _create_record(self, record: DNSRecord, new_ip: str):
        """
        Creates a new DNS record on Cloudflare.
        """
        payload = {
            "type": record.type,
            "name": record.host,
            "content": new_ip,
            "ttl": record.ttl,
            "proxied": False  # Default to False for new records
        }
        try:
            response = httpx.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status()
            data = response.json()
            if not data.get("success"):
                raise Exception(f"Failed to create record {record.host}: {data.get('errors')}")
            print(f"Created record: {record.host} with IP: {new_ip}")
        except httpx.RequestError as e:
            raise Exception(f"Failed to connect to Cloudflare API to create {record.host}: {e}")
        except httpx.HTTPStatusError as e:
            raise Exception(f"Failed to create record {record.host} (status {e.response.status_code}): {e.response.text}")

    def update_records(self, records: List[DNSRecord]):
        """
        Checks and updates/creates the specified DNS records on Cloudflare.
        """
        try:
            public_ip = self._get_public_ip()
            existing_records = self._get_existing_records()

            for record_to_update in records:
                found = False
                for existing_record in existing_records:
                    if existing_record == record_to_update:
                        found = True
                        if existing_record.data != public_ip:
                            self._update_record(existing_record, public_ip)
                        break
                if not found:
                    self._create_record(record_to_update, public_ip)

        except Exception as e:
            print(f"An error occurred during update: {e}")