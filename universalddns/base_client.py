# universalddns/base_client.py
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
        return (self.host == other.host and
                self.type == other.type)

    def __hash__(self):
        return hash((self.host, self.type))

class BaseDDNSClient(abc.ABC):
    """
    Abstract base class for a Dynamic DNS client.
    """
    @abc.abstractmethod
    def update_records(self, records: List[DNSRecord]):
        """
        Updates the specified DNS records.
        """
        pass