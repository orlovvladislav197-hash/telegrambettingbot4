import asyncpg
async def init_db_pool(database_url):
    return await asyncpg.create_pool(database_url)
