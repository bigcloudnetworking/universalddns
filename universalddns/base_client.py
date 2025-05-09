import abc
from typing import List

class DNSRecord(abc.ABC):
    """
    Abstract base class for a DNS record.
    """
    def __init__(self, host: str, type: str, data: str, ttl: int):
        self.host = host
        self.type = type
        self.data = data
        self.ttl = ttl
    
    def __eq__(self, other):
        if not isinstance(other, DNSRecord):
            return NotImplemented
        return (self.host.lower() == other.host.lower() and
                self.type.lower() == other.type.lower())

    def __hash__(self):
        return hash((self.host, self.type))

class BaseDDNSClient(abc.ABC):
    """
    Abstract base class for a Dynamic DNS client.
    """
    @abc.abstractmethod
    def get_records(self) -> List[DNSRecord]:
        """
        Retrieves all DNS records for the zone.
        """
        pass

    @abc.abstractmethod
    def update_record(self, record: DNSRecord, new_data: str) -> None:
        """
        Updates a specific DNS record with new data.
        """
        pass

    @abc.abstractmethod
    def create_record(self, record: DNSRecord) -> None:
        """
        Creates a new DNS record.
        """
        pass

    @abc.abstractmethod
    def delete_record(self, record: DNSRecord) -> None:
         """
         Deletes a DNS record.
         """
         pass

    @abc.abstractmethod
    def update_records(self, records: List[DNSRecord]) -> None:
        """
        Updates the specified DNS records.
        """
        pass