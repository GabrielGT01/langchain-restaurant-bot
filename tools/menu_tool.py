
from typing import Optional
from langchain_core.tools import tool
from tools.schemas import FoodDrinkResult, FoodAgentResponse
from db.database import get_details_category_all

@tool
def menu_prices(category: Optional[str] = None) -> FoodAgentResponse:
    """
    Use this tool to find restaurant menu items, prices, and descriptions.
    The guest states what they want and use this tool to provide varieties
    of what is offered based on each category.
    Use this for any question about menu prices, food details, or what's available.

    Args:
        category: Optional. One of "breakfast", "starters", "mains", "desserts", "drinks".
                  If omitted, returns the full menu.

    Returns a FoodAgentResponse with:
      - answer:      plain-English summary
      - cost:        list of items with name and price
      - description: combined description text for the matching items
    """
    valid_categories = ["breakfast", "starters", "mains", "desserts", "drinks"]
    if category:
        category = category.lower()
        if category not in valid_categories:
            return FoodAgentResponse(
                answer=f"Invalid category. Please choose from: {', '.join(valid_categories)}",
                cost=[], description=""
            )
        items = get_details_category_all(category)
        if not items:
            return FoodAgentResponse(answer=f"No items found for {category}.", cost=[], description="")
        return FoodAgentResponse(
            answer=f"Here are the available {category}.",
            cost=[FoodDrinkResult(item_name=item["item_name"], price=str(item["price"])) for item in items],
            description=" ".join(item["description"] for item in items)
        )
    return FoodAgentResponse(
        answer=f"Please specify a category: {', '.join(valid_categories)}", cost=[], description=""
    )
