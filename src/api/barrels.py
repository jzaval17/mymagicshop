import sqlalchemy
from src import database as db
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from src.api import auth

router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)

class Barrel(BaseModel):
    sku: str

    ml_per_barrel: int
    potion_type: list[int]
    price: int

    quantity: int

@router.post("/deliver/{order_id}")
def post_deliver_barrels(barrels_delivered: list[Barrel], order_id: int):
    with db.engine.begin() as connection:
        # Query current inventory
        result = connection.execute(sqlalchemy.text("SELECT num_green_ml, gold FROM global_inventory WHERE id = 1"))
        inventory = result.fetchone()
        num_green_ml = inventory.num_green_ml
        gold = inventory.gold

        # Calculate the total ml and cost of the barrels
        total_ml_delivered = sum([barrel.ml_per_barrel for barrel in barrels_delivered])
        total_barrel_cost = sum([barrel.price for barrel in barrels_delivered])

        if gold >= total_barrel_cost:
            # Deduct the cost of the barrels from gold and add the ml to inventory
            connection.execute(sqlalchemy.text(f"""
                UPDATE global_inventory 
                SET num_green_ml = num_green_ml + {total_ml_delivered}, 
                    gold = gold - {total_barrel_cost}
                WHERE id = 1
            """))
            return {"status": "Success", "message": f"Delivered {total_ml_delivered} ml and spent {total_barrel_cost} gold"}
        else:
            return {"status": "Failure", "message": "Not enough gold to purchase barrels"}


# Gets called once a day
@router.post("/plan")
def get_wholesale_purchase_plan(wholesale_catalog: list[Barrel]):
    """ """
    print(wholesale_catalog)

    return [
        {
            "sku": "SMALL_RED_BARREL",
            "quantity": 1,
        }
    ]

