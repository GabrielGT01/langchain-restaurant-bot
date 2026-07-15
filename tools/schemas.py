
from typing import List
from pydantic import BaseModel, Field

class FoodDrinkResult(BaseModel):
    item_name: str = Field(description="name of food or drink")
    price:     str = Field(description="Price as a string, e.g. '$14.50'")

class FoodAgentResponse(BaseModel):
    answer:      str                   = Field(description="The agent's answer to the query")
    cost:        List[FoodDrinkResult] = Field(default_factory=list)
    description: str                   = Field(description="food details")

class OpeningHoursResult(BaseModel):
    day:    str = Field(description="day of the week")
    opens:  str = Field(description="opening time")
    closes: str = Field(description="closing time")
    note:   str = Field(description="special note")

class OpeningHoursResponse(BaseModel):
    answer: str                      = Field(description="The agent's answer")
    hours:  List[OpeningHoursResult] = Field(default_factory=list)

class ReservationResult(BaseModel):
    reservation_id: int = Field(description="Unique booking reference number")
    first_name:     str = Field(description="First name of the guest")
    last_name:      str = Field(description="Last name of the guest")
    year:           int = Field(description="Year of the reservation")
    month:          int = Field(description="Month of the reservation")
    day:            int = Field(description="Day of the reservation")
    time:           str = Field(description="Reservation time")
    status:         str = Field(description="'confirmed' or 'cancelled'")

class ReservationAgentResponse(BaseModel):
    answer:       str                     = Field(description="The agent's plain-English answer")
    reservations: List[ReservationResult] = Field(default_factory=list)
