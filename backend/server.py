from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timedelta, time
import math

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Define Models
class BookingCreate(BaseModel):
    area_hectares: float = Field(..., gt=0, description="Mowing area in hectares")
    long_grass: bool = Field(default=False, description="Long grass premium (25% extra)")
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    time: str = Field(..., description="Time in HH:MM format")
    customer_name: str = Field(..., min_length=1)
    customer_phone: str = Field(..., min_length=1)
    customer_address: str = Field(..., min_length=1)

class Booking(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    area_hectares: float
    long_grass: bool
    date: str
    start_time: str
    end_time: str
    customer_name: str
    customer_phone: str
    customer_address: str
    base_price: float
    final_price: float
    work_duration_hours: float
    created_at: datetime = Field(default_factory=datetime.utcnow)

class PriceCalculation(BaseModel):
    area_hectares: float
    work_duration_hours: float
    base_price: float
    final_price: float
    long_grass_premium: float

class AvailableTimesResponse(BaseModel):
    date: str
    available_times: List[str]
    earliest_time: Optional[str]

# Configuration
BASE_PRICE_PER_HECTARE = 27.19  # Base price per hectare
WORK_RATE = 0.4  # hectares per hour
LOGISTICS_TIME = 1.5  # hours between jobs
WORKDAY_START = time(10, 0)  # 10:00 AM
WORKDAY_END = time(20, 0)  # 8:00 PM
LONG_GRASS_PREMIUM = 0.25  # 25% extra for long grass

def calculate_work_duration(area_hectares: float) -> float:
    """Calculate work duration in hours"""
    return area_hectares / WORK_RATE

def calculate_price(area_hectares: float, long_grass: bool = False) -> PriceCalculation:
    """Calculate pricing for the job"""
    work_duration = calculate_work_duration(area_hectares)
    base_price = area_hectares * BASE_PRICE_PER_HECTARE
    
    long_grass_premium = 0.0
    if long_grass:
        long_grass_premium = base_price * LONG_GRASS_PREMIUM
    
    final_price = base_price + long_grass_premium
    
    return PriceCalculation(
        area_hectares=area_hectares,
        work_duration_hours=work_duration,
        base_price=base_price,
        final_price=final_price,
        long_grass_premium=long_grass_premium
    )

def time_to_minutes(time_str: str) -> int:
    """Convert HH:MM to minutes from midnight"""
    hours, minutes = map(int, time_str.split(':'))
    return hours * 60 + minutes

def minutes_to_time(minutes: int) -> str:
    """Convert minutes from midnight to HH:MM"""
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours:02d}:{mins:02d}"

async def get_bookings_for_date(date: str) -> List[Booking]:
    """Get all bookings for a specific date"""
    bookings = await db.bookings.find({"date": date}).sort("start_time", 1).to_list(1000)
    return [Booking(**booking) for booking in bookings]

async def calculate_available_times(date: str) -> AvailableTimesResponse:
    """Calculate available time slots for a given date"""
    # Get existing bookings for the date
    bookings = await get_bookings_for_date(date)
    
    # Start with workday beginning
    workday_start_minutes = time_to_minutes("10:00")
    workday_end_minutes = time_to_minutes("20:00")
    
    # Track occupied time slots
    occupied_slots = []
    
    for booking in bookings:
        start_minutes = time_to_minutes(booking.start_time)
        end_minutes = time_to_minutes(booking.end_time)
        occupied_slots.append((start_minutes, end_minutes))
    
    # Sort occupied slots by start time
    occupied_slots.sort()
    
    # Find available slots
    available_times = []
    current_time = workday_start_minutes
    
    for start, end in occupied_slots:
        # Add times before this booking
        while current_time < start:
            if current_time + 60 <= workday_end_minutes:  # At least 1 hour slots
                available_times.append(minutes_to_time(current_time))
            current_time += 30  # 30-minute intervals
        
        # Skip to after this booking
        current_time = max(current_time, end)
    
    # Add remaining times after last booking
    while current_time < workday_end_minutes:
        if current_time + 60 <= workday_end_minutes:
            available_times.append(minutes_to_time(current_time))
        current_time += 30
    
    # If no times available, find earliest time
    earliest_time = None
    if not available_times and occupied_slots:
        # Find the earliest time after all bookings
        last_end = max(end for _, end in occupied_slots)
        if last_end < workday_end_minutes:
            earliest_time = minutes_to_time(last_end)
    elif available_times:
        earliest_time = available_times[0]
    else:
        earliest_time = "10:00"
    
    return AvailableTimesResponse(
        date=date,
        available_times=available_times,
        earliest_time=earliest_time
    )

@api_router.post("/calculate-price", response_model=PriceCalculation)
async def calculate_job_price(area_hectares: float, long_grass: bool = False):
    """Calculate price for a mowing job"""
    if area_hectares <= 0:
        raise HTTPException(status_code=400, detail="Area must be greater than 0")
    
    return calculate_price(area_hectares, long_grass)

@api_router.get("/available-times/{date}", response_model=AvailableTimesResponse)
async def get_available_times(date: str):
    """Get available time slots for a specific date"""
    try:
        # Validate date format
        datetime.strptime(date, '%Y-%m-%d')
        return await calculate_available_times(date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

@api_router.post("/bookings", response_model=Booking)
async def create_booking(booking_data: BookingCreate):
    """Create a new booking"""
    try:
        # Validate date format
        datetime.strptime(booking_data.date, '%Y-%m-%d')
        
        # Validate time format
        time_obj = datetime.strptime(booking_data.time, '%H:%M').time()
        
        # Check if time is within work hours
        if time_obj < WORKDAY_START or time_obj > WORKDAY_END:
            raise HTTPException(status_code=400, detail="Time must be between 10:00 and 20:00")
        
        # Check if the requested time is available
        available_times = await calculate_available_times(booking_data.date)
        if booking_data.time not in available_times.available_times:
            raise HTTPException(
                status_code=400, 
                detail=f"Time {booking_data.time} is not available. Available times: {available_times.available_times}"
            )
        
        # Calculate pricing and duration
        price_calc = calculate_price(booking_data.area_hectares, booking_data.long_grass)
        work_duration = price_calc.work_duration_hours
        
        # Calculate end time (work duration + logistics time)
        start_minutes = time_to_minutes(booking_data.time)
        total_duration_minutes = int((work_duration + LOGISTICS_TIME) * 60)
        end_minutes = start_minutes + total_duration_minutes
        end_time = minutes_to_time(end_minutes)
        
        # Create booking object
        booking = Booking(
            area_hectares=booking_data.area_hectares,
            long_grass=booking_data.long_grass,
            date=booking_data.date,
            start_time=booking_data.time,
            end_time=end_time,
            customer_name=booking_data.customer_name,
            customer_phone=booking_data.customer_phone,
            customer_address=booking_data.customer_address,
            base_price=price_calc.base_price,
            final_price=price_calc.final_price,
            work_duration_hours=work_duration
        )
        
        # Save to database
        await db.bookings.insert_one(booking.dict())
        
        return booking
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid date or time format: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating booking: {str(e)}")

@api_router.get("/bookings", response_model=List[Booking])
async def get_all_bookings():
    """Get all bookings"""
    bookings = await db.bookings.find().sort("date", 1).sort("start_time", 1).to_list(1000)
    return [Booking(**booking) for booking in bookings]

@api_router.get("/bookings/{date}", response_model=List[Booking])
async def get_bookings_by_date(date: str):
    """Get bookings for a specific date"""
    try:
        datetime.strptime(date, '%Y-%m-%d')
        bookings = await get_bookings_for_date(date)
        return bookings
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()