import os, asyncio
from web3 import Web3
from dotenv import load_dotenv
import asyncpg
from datetime import datetime
from decimal import Decimal

load_dotenv()
RPC = os.getenv('RPC_URL')
DATABASE_URL = os.getenv('DATABASE_URL')
CONFIRMATIONS = int(os.getenv('CONFIRMATIONS', '3'))

w3 = Web3(Web3.HTTPProvider(RPC))

async def main():
    pool = await asyncpg.create_pool(DATABASE_URL)
    last_checked = w3.eth.block_number - 1
    while True:
        latest = w3.eth.block_number
        for bnum in range(last_checked+1, latest+1):
            block = w3.eth.get_block(bnum, full_transactions=True)
            for tx in block.transactions:
                to = tx.to
                if not to:
                    continue
                checksum = Web3.toChecksumAddress(to)
                async with pool.acquire() as conn:
                    row = await conn.fetchrow('SELECT id, user_id FROM deposit_addresses WHERE address=$1 AND active=true', checksum)
                    if row:
                        exists = await conn.fetchrow('SELECT id FROM deposits WHERE tx_hash=$1', tx.hash.hex())
                        if exists:
                            continue
                        await conn.execute('INSERT INTO deposits(address_id, tx_hash, amount, currency, confirmed, detected_at) VALUES($1,$2,$3,$4,$5,$6)', row['id'], tx.hash.hex(), Decimal(w3.fromWei(tx.value, "ether")), 'ETH', False, datetime.utcnow())
        async with pool.acquire() as conn:
            pending = await conn.fetch('SELECT d.id, d.tx_hash, d.amount, a.user_id FROM deposits d JOIN deposit_addresses a ON d.address_id = a.id WHERE d.confirmed = false')
            for p in pending:
                try:
                    tx_receipt = w3.eth.get_transaction_receipt(p['tx_hash'])
                except Exception:
                    continue
                if tx_receipt and latest - tx_receipt.blockNumber + 1 >= CONFIRMATIONS:
                    async with conn.transaction():
                        await conn.execute('UPDATE deposits SET confirmed=true WHERE id=$1', p['id'])
                        await conn.execute('UPDATE users SET balance = balance + $1 WHERE id = $2', p['amount'], p['user_id'])
        last_checked = latest
        await asyncio.sleep(5)

if __name__ == '__main__':
    asyncio.run(main())
