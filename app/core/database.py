import os
from psycopg_pool import AsyncConnectionPool
from psycopg.rows import dict_row
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/travel_db")

# Async connection pool for application queries (Auth & Users)
db_pool = AsyncConnectionPool(
    conninfo=DATABASE_URL,
    max_size=10,
    #open=False,
    kwargs={"autocommit": True, "row_factory": dict_row}
)

async def init_db():
    """
    1. Creates users table for JWT authentication if not exists.
    2. Initializes LangGraph checkpoint tables in PostgreSQL.
    """
    await db_pool.wait() # waits for a connection
    async with db_pool.connection() as conn:
        # Create Users table for JWT authentication
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL,
                full_name VARCHAR(255),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """)

    # Initialize LangGraph checkpoint tables (checkpoints, checkpoint_blobs, checkpoint_writes)
    async with AsyncPostgresSaver.from_conn_string(DATABASE_URL) as checkpointer:
        await checkpointer.setup()