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

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Estonian Lawn Mowing API is running!", "status": "healthy"}

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

class BookedSlot(BaseModel):
    start_time: str
    end_time: str
    customer_name: str
    area_hectares: float

class AvailableTimesResponse(BaseModel):
    date: str
    available_times: List[str]
    booked_slots: List[BookedSlot]
    earliest_time: Optional[str]

# Service Provider Models
class ServiceProviderCreate(BaseModel):
    name: str = Field(..., min_length=1)
    phone: str = Field(..., min_length=1)
    email: str = Field(..., min_length=1)
    specialization: str = Field(default="general")  # general, large_areas, precision, etc.
    hourly_rate: float = Field(..., gt=0)
    max_area_per_day: float = Field(default=10.0)
    working_days: List[int] = Field(default=[0, 1, 2, 3, 4])  # Monday to Friday
    start_time: str = Field(default="08:00")
    end_time: str = Field(default="18:00")
    is_active: bool = Field(default=True)

class ServiceProvider(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    phone: str
    email: str
    specialization: str
    hourly_rate: float
    max_area_per_day: float
    working_days: List[int]
    start_time: str
    end_time: str
    is_active: bool
    created_at: datetime = Field(default_factory=datetime.utcnow)
    total_jobs_completed: int = Field(default=0)
    average_rating: float = Field(default=5.0)

# Work Assignment Models
class WorkAssignmentCreate(BaseModel):
    booking_id: str
    provider_id: str
    scheduled_date: str
    scheduled_time: str
    estimated_duration: float
    special_instructions: Optional[str] = None

class WorkAssignment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    booking_id: str
    provider_id: str
    scheduled_date: str
    scheduled_time: str
    estimated_duration: float
    special_instructions: Optional[str]
    status: str = Field(default="assigned")  # assigned, in_progress, completed, cancelled
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    rating: Optional[float] = None
    feedback: Optional[str] = None

# Configuration - WORKING DAYS: Monday to Friday
BASE_PRICE_PER_HECTARE = 27.19  # Base price per hectare
WORK_RATE = 0.4  # hectares per hour
LOGISTICS_TIME = 1.5  # hours between jobs
WORKDAY_START = time(8, 0)  # 8:00 AM
WORKDAY_END = time(18, 0)  # 6:00 PM
LONG_GRASS_PREMIUM = 0.25  # 25% extra for long grass
WORKING_DAYS = [0, 1, 2, 3, 4]  # Monday to Friday (0=Monday, 6=Sunday)

def is_working_day(date_str: str) -> bool:
    """Check if the date is a working day (Monday to Friday)"""
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    return date_obj.weekday() in WORKING_DAYS

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

def calculate_latest_start_time(work_duration_hours: float) -> str:
    """Calculate the latest possible start time for a job to finish by 18:00"""
    workday_end_minutes = time_to_minutes("18:00")
    total_job_time_minutes = int(work_duration_hours * 60)  # Only work time, no logistics needed for last job
    latest_start_minutes = workday_end_minutes - total_job_time_minutes
    
    # Ensure it's not before workday start
    workday_start_minutes = time_to_minutes("08:00")
    if latest_start_minutes < workday_start_minutes:
        latest_start_minutes = workday_start_minutes
    
    return minutes_to_time(latest_start_minutes)

async def get_bookings_for_date(date: str) -> List[Booking]:
    """Get all bookings for a specific date"""
    bookings = await db.bookings.find({"date": date}).sort("start_time", 1).to_list(1000)
    return [Booking(**booking) for booking in bookings]

async def calculate_available_times(date: str, area_hectares: float = 1.0) -> AvailableTimesResponse:
    """Calculate available time slots for a given date and area"""
    # Check if it's a working day
    if not is_working_day(date):
        return AvailableTimesResponse(
            date=date,
            available_times=[],
            booked_slots=[],
            earliest_time=None
        )
    
    # Get existing bookings for the date
    bookings = await get_bookings_for_date(date)
    
    # Create booked slots info
    booked_slots = []
    for booking in bookings:
        booked_slots.append(BookedSlot(
            start_time=booking.start_time,
            end_time=booking.end_time,
            customer_name=booking.customer_name,
            area_hectares=booking.area_hectares
        ))
    
    # Calculate work duration for the requested area
    work_duration = calculate_work_duration(area_hectares)
    
    # Calculate latest possible start time
    latest_start = calculate_latest_start_time(work_duration)
    latest_start_minutes = time_to_minutes(latest_start)
    
    # Start with workday beginning
    workday_start_minutes = time_to_minutes("08:00")
    workday_end_minutes = time_to_minutes("18:00")
    
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
        while current_time < start and current_time <= latest_start_minutes:
            # Check if there's enough time for the job
            job_end_time = current_time + int(work_duration * 60)
            if job_end_time <= workday_end_minutes:
                available_times.append(minutes_to_time(current_time))
            current_time += 30  # 30-minute intervals
        
        # Skip to after this booking
        current_time = max(current_time, end)
    
    # Add remaining times after last booking
    while current_time <= latest_start_minutes:
        job_end_time = current_time + int(work_duration * 60)
        if job_end_time <= workday_end_minutes:
            available_times.append(minutes_to_time(current_time))
        current_time += 30
    
    # Find earliest time
    earliest_time = None
    if available_times:
        earliest_time = available_times[0]
    elif not occupied_slots:
        earliest_time = "08:00"
    else:
        # Find the earliest time after all bookings
        last_end = max(end for _, end in occupied_slots)
        if last_end <= latest_start_minutes:
            earliest_time = minutes_to_time(last_end)
    
    return AvailableTimesResponse(
        date=date,
        available_times=available_times,
        booked_slots=booked_slots,
        earliest_time=earliest_time
    )

@api_router.post("/calculate-price", response_model=PriceCalculation)
async def calculate_job_price(area_hectares: float, long_grass: bool = False):
    """Calculate price for a mowing job"""
    if area_hectares <= 0:
        raise HTTPException(status_code=400, detail="Area must be greater than 0")
    
    return calculate_price(area_hectares, long_grass)

@api_router.get("/available-times/{date}", response_model=AvailableTimesResponse)
async def get_available_times(date: str, area_hectares: float = 1.0):
    """Get available time slots for a specific date and area"""
    try:
        # Validate date format
        datetime.strptime(date, '%Y-%m-%d')
        return await calculate_available_times(date, area_hectares)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

@api_router.post("/bookings", response_model=Booking)
async def create_booking(booking_data: BookingCreate):
    """Create a new booking"""
    try:
        # Validate date format
        datetime.strptime(booking_data.date, '%Y-%m-%d')
        
        # Check if it's a working day
        if not is_working_day(booking_data.date):
            raise HTTPException(status_code=400, detail="Töötame ainult esmaspäevast reedeni")
        
        # Validate time format
        time_obj = datetime.strptime(booking_data.time, '%H:%M').time()
        
        # Check if time is within work hours and allows job completion
        work_duration = calculate_work_duration(booking_data.area_hectares)
        latest_start = calculate_latest_start_time(work_duration)
        
        if time_obj < WORKDAY_START or booking_data.time > latest_start:
            raise HTTPException(
                status_code=400, 
                detail=f"Time must be between 08:00 and {latest_start} for {booking_data.area_hectares}ha area"
            )
        
        # Check if the requested time is available
        available_times = await calculate_available_times(booking_data.date, booking_data.area_hectares)
        if booking_data.time not in available_times.available_times:
            raise HTTPException(
                status_code=400, 
                detail=f"Time {booking_data.time} is not available for {booking_data.area_hectares}ha. Available times: {available_times.available_times}"
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