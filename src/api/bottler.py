import sqlalchemy
from src import database as db
from fastapi import APIRouter, Depends
from enum import Enum
from pydantic import BaseModel
from src.api import auth

router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)

class PotionInventory(BaseModel):
    potion_type: list[int]
    quantity: int

@router.post("/mix/")
def post_mix_potions():
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT num_green_ml, num_green_potions FROM global_inventory WHERE id = 1"))
        inventory = result.fetchone()
        num_green_ml = inventory.num_green_ml
        potion_volume = 100  # Assume each potion requires 100ml

        potions_mixed = num_green_ml // potion_volume

        if potions_mixed > 0:
            # Update inventory with new potions and deduct ml used
            connection.execute(sqlalchemy.text(f"""
                UPDATE global_inventory
                SET num_green_potions = num_green_potions + {potions_mixed},
                    num_green_ml = num_green_ml - ({potions_mixed} * {potion_volume})
                WHERE id = 1
            """))
            return {"status": "Success", "message": f"Mixed {potions_mixed} green potions"}
        else:
            return {"status": "Failure", "message": "Not enough ml to mix potions"}

@router.post("/deliver/{order_id}")
def post_deliver_bottles(potions_delivered: list[PotionInventory], order_id: int):
    """ """
    print(f"potions delievered: {potions_delivered} order_id: {order_id}")

    return "OK"

@router.post("/plan")
def get_bottle_plan():
    """
    Go from barrel to bottle.
    Dynamically calculate potion quantity based on available ml in the inventory.
    """

    # Define how much ml is required to create one potion
    potion_volume = 100  # ml per potion

    # Connect to the database and get the current ml in inventory
    with db.engine.begin() as connection:
        result = connection.execute(sqlalchemy.text("SELECT num_green_ml FROM global_inventory WHERE id = 1"))
        inventory = result.fetchone()

        num_green_ml = inventory.num_green_ml

    # Calculate how many potions can be made
    quantity = num_green_ml // potion_volume  # Integer division to get whole potions

    # If there's enough ml for at least one potion, return that; otherwise, return 0
    if quantity > 0:
        return [
            {
                "potion_type": [0, 100, 0, 0],  # This represents 100% green potions
                "quantity": quantity,           # Dynamically calculated quantity
            }
        ]
    else:
        return {
            "status": "Failure",
            "message": "Not enough ml to bottle potions. You need more potion liquid."
        }

if __name__ == "__main__":
    print(get_bottle_plan())