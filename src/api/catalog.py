import sqlalchemy
from src import database as db
from fastapi import APIRouter

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT num_green_potions FROM global_inventory WHERE id = 1"))
        inventory = result.fetchone()

        num_green_potions = inventory.num_green_potions

        return [
            {
                "sku": "GREEN_POTION_0",
                "name": "green potion",
                "quantity": num_green_potions,
                "price": 50,  # Assume each green potion costs 50 gold
                "potion_type": [0, 100, 0, 0],  # Example type for green potion
            }
        ]
