from fastapi import HTTPException
from config.database import get_postgres_conn


class AdminModel:
    """Model for handling admin operations in PostgreSQL."""

    @staticmethod
    async def update_user(user_data: dict) -> None:
        """Update user data in PostgreSQL."""
        conn = get_postgres_conn()
        try:
            with conn.cursor() as cur:
                update_fields = []
                values = []
                for key, value in user_data.items():
                    if key != "user_id" and value is not None:
                        update_fields.append(f"{key} = %s")
                        values.append(value)
                if not update_fields:
                    raise HTTPException(
                        status_code=400, detail="No fields to update")
                values.append(user_data["user_id"])
                query = f"UPDATE user SET {', '.join(update_fields)} WHERE user_id = %s"
                cur.execute(query, values)
                if cur.rowcount == 0:
                    raise HTTPException(
                        status_code=404, detail="User not found")
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    async def update_game(game_data: dict) -> None:
        """Update game data in PostgreSQL."""
        conn = get_postgres_conn()
        try:
            with conn.cursor() as cur:
                update_fields = []
                values = []
                for key, value in user_data.items():
                    if key != "game_id" and value is not None:
                        update_fields.append(f"{key} = %s")
                        values.append(value)
                if not update_fields:
                    raise HTTPException(
                        status_code=400, detail="No fields to update")
                values.append(game_data["game_id"])
                query = f"UPDATE game SET {', '.join(update_fields)} WHERE game_id = %s"
                cur.execute(query, values)
                if cur.rowcount == 0:
                    raise HTTPException(
                        status_code=404, detail="Game not found")
            conn.commit()
        finally:
            conn.close()
