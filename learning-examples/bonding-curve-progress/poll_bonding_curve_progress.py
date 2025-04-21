"""
Module for tracking the progress of a bonding curve for a Pump.fun token.
It continuously polls the bonding curve state and prints updates at regular intervals.
"""

import asyncio
import os
import struct
from typing import Final

from dotenv import load_dotenv
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey

load_dotenv()

# Constants
RPC_URL: Final[str] = os.getenv("SOLANA_NODE_RPC_ENDPOINT")
TOKEN_MINT: Final[str] = "xWrzYY4c1LnbSkLrd2LDUg9vw7YtVyJhGmw7MABpump"
PUMP_PROGRAM_ID: Final[Pubkey] = Pubkey.from_string("6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P")
LAMPORTS_PER_SOL: Final[int] = 1_000_000_000
TOKEN_DECIMALS: Final[int] = 6
EXPECTED_DISCRIMINATOR: Final[bytes] = struct.pack("<Q", 6966180631402821399)  # Pump.fun bonding curve discriminator
POLL_INTERVAL: Final[int] = 10  # Seconds between each status check


def get_associated_bonding_curve_address(mint: Pubkey, program_id: Pubkey) -> Pubkey:
    """
    Derive the bonding curve PDA address from a mint address.
    
    Args:
        mint: The token mint address
        program_id: The program ID for the bonding curve
        
    Returns:
        The bonding curve address
    """
    return Pubkey.find_program_address([b"bonding-curve", bytes(mint)], program_id)[0]


async def get_account_data(client: AsyncClient, pubkey: Pubkey) -> bytes:
    """
    Fetch raw account data for a given public key.
    
    Args:
        client: AsyncClient connection to Solana RPC
        pubkey: The public key of the account to fetch
        
    Returns:
        The raw account data as bytes
        
    Raises:
        ValueError: If the account is not found or has no data
    """
    resp = await client.get_account_info(pubkey, encoding="base64")
    if not resp.value or not resp.value.data:
        raise ValueError(f"Account {pubkey} not found or has no data")

    return resp.value.data


def parse_curve_state(data: bytes) -> dict:
    """
    Decode bonding curve account data into a readable format.
    
    Args:
        data: The raw bonding curve account data
        
    Returns:
        A dictionary containing parsed bonding curve fields
        
    Raises:
        ValueError: If the account discriminator is invalid
    """
    if data[:8] != EXPECTED_DISCRIMINATOR:
        raise ValueError("Invalid discriminator for bonding curve")

    fields = struct.unpack_from("<QQQQQ?", data, 8)
    return {
        "virtual_token_reserves": fields[0] / 10**TOKEN_DECIMALS,
        "virtual_sol_reserves": fields[1] / LAMPORTS_PER_SOL,
        "real_token_reserves": fields[2] / 10**TOKEN_DECIMALS,
        "real_sol_reserves": fields[3] / LAMPORTS_PER_SOL,
        "token_total_supply": fields[4] / 10**TOKEN_DECIMALS,
        "complete": fields[5],
    }


def print_curve_status(state: dict) -> None:
    """
    Print the current status of the bonding curve in a readable format.
    
    Args:
        state: The parsed bonding curve state dictionary
    """
    progress = 0
    if state["token_total_supply"]:
        progress = 100 - (100 * state["real_token_reserves"] / state["token_total_supply"])

    print("=" * 30)
    print(f"Complete: {'✅' if state['complete'] else '❌'}")
    print(f"Progress: {progress:.2f}%")
    print(f"Token reserves: {state['real_token_reserves']:.4f}")
    print(f"SOL reserves:   {state['real_sol_reserves']:.4f}")
    print("=" * 30, "\n")


async def track_curve() -> None:
    """
    Continuously track and display the state of a bonding curve.
    """
    if not RPC_URL or not TOKEN_MINT:
        print("❌ Set SOLANA_NODE_RPC_ENDPOINT and TOKEN_MINT in .env")
        return

    mint_pubkey: Pubkey = Pubkey.from_string(TOKEN_MINT)
    curve_pubkey: Pubkey = get_associated_bonding_curve_address(mint_pubkey, PUMP_PROGRAM_ID)

    print("Tracking bonding curve for:", mint_pubkey)
    print("Curve address:", curve_pubkey, "\n")

    async with AsyncClient(RPC_URL) as client:
        while True:
            try:
                data = await get_account_data(client, curve_pubkey)
                state = parse_curve_state(data)
                print_curve_status(state)
            except Exception as e:
                print(f"⚠️ Error: {e}")

            await asyncio.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    asyncio.run(track_curve())
