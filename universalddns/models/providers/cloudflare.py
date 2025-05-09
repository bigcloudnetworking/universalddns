import httpx
import logging
from typing import List
from universalddns.base_client import BaseDDNSClient, DNSRecord


class CloudflareRecord(DNSRecord):
    """
    Represents a Cloudflare DNS record.
    """

    def __init__(
            self,
            host: str,
            type: str,
            data: str,
            ttl: int,
            record_id: str = None,
            proxied: bool = False):
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
        self.api_url = (
            f"https://api.cloudflare.com/client/v4/zones/"
            f"{self.zone_id}/dns_records"
        )
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        self.logger = logging.getLogger(__name__)  # Get a logger for this class

    def _get_public_ip(self) -> str:
        """
        Gets the current public IP address using ipconfig.io.
        """
        try:
            response = httpx.get("https://ipconfig.io/ip", timeout=5)
            response.raise_for_status()
            ip_address = response.text.strip()
            self.logger.debug(
                f"Retrieved public IP address: {ip_address}")  # Log the IP
            return ip_address
        except httpx.RequestError as e:
            self.logger.error(f"Failed to connect to get public IP: {e}")
            raise Exception(f"Failed to connect to get public IP: {e}")
        except httpx.HTTPStatusError as e:
            self.logger.error(
                "Failed to get public IP (status"
                f" {e.response.status_code}): {e.response.text}"
            )
            raise Exception(
                "Failed to get public IP (status"
                f" {e.response.status_code}): {e.response.text}"
            )

    def get_records(self) -> List[DNSRecord]:
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
                self.logger.debug(
                    f"Retrieved {len(records)} Cloudflare records.")  # Log record count
                return records
            else:
                self.logger.error(
                    f"Failed to get Cloudflare records: {data.get('errors')}")
                raise Exception(
                    f"Failed to get Cloudflare records: {data.get('errors')}")
        except httpx.RequestError as e:
            self.logger.error(f"Failed to connect to Cloudflare API: {e}")
            raise Exception(f"Failed to connect to Cloudflare API: {e}")
        except httpx.HTTPStatusError as e:
            self.logger.error(
                "Failed to get Cloudflare records (status"
                f" {e.response.status_code}): {e.response.text}"
            )
            raise Exception(
                "Failed to get Cloudflare records (status"
                f" {e.response.status_code}): {e.response.text}"
            )

    def update_record(self, record: DNSRecord, new_data: str) -> None:
        """
        Updates a specific DNS record with new data on Cloudflare.
        """
        if not isinstance(record, CloudflareRecord):
            raise ValueError("Record must be a CloudflareRecord")

        payload = {
            "type": record.type,
            "name": record.host,
            "content": new_data,
            "ttl": record.ttl,
            "proxied": record.proxied
        }
        try:
            url = f"{self.api_url}/{record.record_id}"
            response = httpx.put(url, headers=self.headers, json=payload)
            response.raise_for_status()
            data = response.json()
            if not data.get("success"):
                self.logger.error(
                    f"Failed to update record {record.host}: {data.get('errors')}")
                raise Exception(
                    f"Failed to update record {record.host}: {data.get('errors')}")
            self.logger.info(f"Updated record: {record.host} to {new_data}")
        except httpx.RequestError as e:
            self.logger.error(
                "Failed to connect to Cloudflare API to update"
                f" {record.host}: {e}"
            )
            raise Exception(
                "Failed to connect to Cloudflare API to update"
                f" {record.host}: {e}"
            )
        except httpx.HTTPStatusError as e:
            self.logger.error(
                "Failed to update record {record.host} (status"
                f" {e.response.status_code}): {e.response.text}"
            )
            raise Exception(
                "Failed to update record {record.host} (status"
                f" {e.response.status_code}): {e.response.text}"
            )

    def create_record(self, record: DNSRecord) -> None:
        """
        Creates a new DNS record on Cloudflare.
        """
        new_ip = self._get_public_ip()  # fetch IP here so we don't have to pass it as param
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
                self.logger.error(
                    f"Failed to create record {record.host}: {data.get('errors')}")
                raise Exception(
                    f"Failed to create record {record.host}: {data.get('errors')}")
            self.logger.info(f"Created record: {record.host} with IP: {new_ip}")
        except httpx.RequestError as e:
            self.logger.error(
                "Failed to connect to Cloudflare API to create"
                f" {record.host}: {e}"
            )
            raise Exception(
                "Failed to connect to Cloudflare API to create"
                f" {record.host}: {e}"
            )
        except httpx.HTTPStatusError as e:
            self.logger.error(
                "Failed to create record {record.host} (status"
                f" {e.response.status_code}): {e.response.text}"
            )
            raise Exception(
                "Failed to create record {record.host} (status"
                f" {e.response.status_code}): {e.response.text}"
            )

    def delete_record(self, record: DNSRecord) -> None:
        """
        Deletes a DNS record from Cloudflare.
        """
        if not isinstance(record, CloudflareRecord):
            raise ValueError("Record must be a CloudflareRecord")

        try:
            url = f"{self.api_url}/{record.record_id}"
            response = httpx.delete(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            if not data.get("success"):
                self.logger.error(
                    f"Failed to delete record {record.host}: {data.get('errors')}")
                raise Exception(
                    f"Failed to delete record {record.host}: {data.get('errors')}")
            self.logger.info(f"Deleted record: {record.host}")
        except httpx.RequestError as e:
            self.logger.error(
                "Failed to connect to Cloudflare API to delete"
                f" {record.host}: {e}"
            )
            raise Exception(
                "Failed to connect to Cloudflare API to delete"
                f" {record.host}: {e}"
            )
        except httpx.HTTPStatusError as e:
            self.logger.error(
                "Failed to delete record {record.host} (status"
                f" {e.response.status_code}): {e.response.text}"
            )
            raise Exception(
                "Failed to delete record {record.host} (status"
                f" {e.response.status_code}): {e.response.text}"
            )

    def update_records(self, records: List[DNSRecord]):
        """
        Checks and updates/creates the specified DNS records on Cloudflare.
        """
        try:
            public_ip = self._get_public_ip()
            existing_records = self.get_records()

            for record_to_update in records:
                found = False
                for existing_record in existing_records:
                    if existing_record == record_to_update:
                        found = True
                        if existing_record.data != public_ip:
                            self.update_record(
                                record=existing_record, new_data=public_ip)
                        break
                if not found:
                    self.create_record(record=record_to_update)

        except Exception as e:
            self.logger.error(f"An error occurred during update: {e}")