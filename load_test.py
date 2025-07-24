import asyncio
from pymongo import AsyncMongoClient
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.errors import PyMongoError
from dotenv import load_dotenv
import os
import time
from statistics import mean, quantiles

load_dotenv()

# ─── CONFIGURATION ────────────────────────────────────────────────────────────
MONGO_URI       = os.environ["DATABASE_URI"]
DB_NAME         = "loadtest_db"
COLL_NAME       = "loadtest_coll"
TOTAL_OPS       = 5000                    # total inserts per concurrency level
CONCURRENCIES   = [1, 5, 10, 20, 50, 100]  # concurrency levels to test
MAX_POOL        = 200                    # maxPoolSize on the client
MAX_CONNECTING  = 4
# ──────────────────────────────────────────────────────────────────────────────

client = AsyncMongoClient(
    MONGO_URI,
    maxPoolSize = MAX_POOL,
    maxConnecting = MAX_CONNECTING
)

async def single_write(loadtest_collection: AsyncCollection):
    start = time.perf_counter()
    try:
        await loadtest_collection.insert_one({"x": 1})
        end = time.perf_counter()
        return end - start, True
    except PyMongoError as e:
        print(f"Failed to insert: {e}")
        end = time.perf_counter()
        return end - start, False

async def load_test(concurrency: int, loadtest_collection: AsyncCollection, total_operations: int):
    print(f"Concurrency level: {concurrency}")
    print(f"Total operations: {total_operations}")
    semaphore = asyncio.Semaphore(concurrency)
    async with semaphore:
        write_operations = []
        for _ in range(total_operations):
            write_operations.append(single_write(loadtest_collection=loadtest_collection))
        results = await asyncio.gather(*write_operations)
        latencies = [result[0] for result in results]
        qs = quantiles(latencies, n=100)
        mean_latency = mean(latencies)
        p95 = qs[94]
        print(f"Mean latency: {mean_latency}")
        print(f"p95: {p95}")

async def connect_db(db_client: AsyncMongoClient):
    try:
        await db_client.admin.command("ping")
        print("Database is connected")
    except PyMongoError as error:
        print(f"Failed to connect DB: {error}")
    

async def main():
    print("Load test is processing ...")

    await connect_db(client)

    loadtest_database = client[DB_NAME]
    loadtest_collection = loadtest_database[COLL_NAME]
    
    print("Cleaning up ...")
    await loadtest_collection.delete_many({})
    print("database is cleaned")

    await load_test(concurrency=50000, loadtest_collection=loadtest_collection, total_operations=TOTAL_OPS)

    print("Load test is finished")

if __name__ == "__main__":
    asyncio.run(main())