from typing import List
from sqlalchemy.orm import Session
from DB.create_database import connect_db
from DB.models import Gift
import json

 
def get_nfts_by_prefix(prefix: str) -> Gift:
    """
    Return the number of Gift records whose name starts with the given prefix.

    Args:
        prefix (str): Prefix to match at the start of Gift.name.

    Returns:
        int: Count of Gift records where name LIKE "<prefix>%".
    """
    with connect_db() as session:
        nfts = session.query(Gift).filter(Gift.name.like(f"{prefix}%")).count()
        return nfts


def calculate_rarity(nft, collection_stats):
    return None


if __name__ == "__main__":
    print(get_nfts_by_prefix("Plush Pepe"))