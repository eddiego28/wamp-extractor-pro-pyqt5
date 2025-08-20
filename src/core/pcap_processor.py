
# -*- coding: utf-8 -*-
from typing import List, Dict
from .pcap_parser import Filters, extract_messages

def process_pcap_to_records(pcap_path: str, filters: Filters) -> List[Dict]:
    return extract_messages(pcap_path, filters)
