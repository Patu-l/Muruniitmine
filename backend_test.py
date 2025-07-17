#!/usr/bin/env python3
"""
Comprehensive backend testing for Estonian lawn mowing booking system
Tests all API endpoints and business logic validation
"""

import requests
import json
from datetime import datetime, timedelta
import sys
import os

# Get backend URL from frontend .env file
def get_backend_url():
    try:
        with open('/app/frontend/.env', 'r') as f:
            for line in f:
                if line.startswith('REACT_APP_BACKEND_URL='):
                    return line.split('=', 1)[1].strip()
    except Exception as e:
        print(f"Error reading backend URL: {e}")
        return None

BASE_URL = get_backend_url()
if not BASE_URL:
    print("ERROR: Could not get backend URL from frontend/.env")
    sys.exit(1)

API_BASE = f"{BASE_URL}/api"

print(f"Testing backend at: {API_BASE}")

class TestResults:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def test_pass(self, test_name):
        self.passed += 1
        print(f"✅ PASS: {test_name}")
    
    def test_fail(self, test_name, error):
        self.failed += 1
        self.errors.append(f"{test_name}: {error}")
        print(f"❌ FAIL: {test_name} - {error}")
    
    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'='*60}")
        print(f"TEST SUMMARY: {self.passed}/{total} tests passed")
        if self.errors:
            print(f"\nFAILED TESTS:")
            for error in self.errors:
                print(f"  - {error}")
        print(f"{'='*60}")
        return self.failed == 0

results = TestResults()

def test_price_calculation():
    """Test price calculation endpoint with various scenarios"""
    print("\n🧮 Testing Price Calculation API...")
    
    # Test 1: Basic price calculation
    try:
        response = requests.post(f"{API_BASE}/calculate-price", params={
            "area_hectares": 1.0,
            "long_grass": False
        })
        if response.status_code == 200:
            data = response.json()
            expected_base_price = 1.0 * 27.19  # 27.19€
            expected_work_duration = 1.0 / 0.4  # 2.5 hours
            
            if abs(data["base_price"] - expected_base_price) < 0.01:
                results.test_pass("Basic price calculation (1 hectare)")
            else:
                results.test_fail("Basic price calculation", f"Expected {expected_base_price}, got {data['base_price']}")
            
            if abs(data["work_duration_hours"] - expected_work_duration) < 0.01:
                results.test_pass("Work duration calculation (1 hectare)")
            else:
                results.test_fail("Work duration calculation", f"Expected {expected_work_duration}, got {data['work_duration_hours']}")
        else:
            results.test_fail("Basic price calculation API", f"Status {response.status_code}")
    except Exception as e:
        results.test_fail("Basic price calculation API", str(e))
    
    # Test 2: Long grass premium
    try:
        response = requests.post(f"{API_BASE}/calculate-price", params={
            "area_hectares": 2.0,
            "long_grass": True
        })
        if response.status_code == 200:
            data = response.json()
            expected_base_price = 2.0 * 27.19  # 54.38€
            expected_premium = expected_base_price * 0.25  # 25% premium
            expected_final_price = expected_base_price + expected_premium
            
            if abs(data["final_price"] - expected_final_price) < 0.01:
                results.test_pass("Long grass premium calculation")
            else:
                results.test_fail("Long grass premium", f"Expected {expected_final_price}, got {data['final_price']}")
        else:
            results.test_fail("Long grass premium API", f"Status {response.status_code}")
    except Exception as e:
        results.test_fail("Long grass premium API", str(e))
    
    # Test 3: Invalid area (negative)
    try:
        response = requests.post(f"{API_BASE}/calculate-price", params={
            "area_hectares": -1.0,
            "long_grass": False
        })
        if response.status_code == 400:
            results.test_pass("Negative area validation")
        else:
            results.test_fail("Negative area validation", f"Expected 400, got {response.status_code}")
    except Exception as e:
        results.test_fail("Negative area validation", str(e))
    
    # Test 4: Zero area
    try:
        response = requests.post(f"{API_BASE}/calculate-price", params={
            "area_hectares": 0.0,
            "long_grass": False
        })
        if response.status_code == 400:
            results.test_pass("Zero area validation")
        else:
            results.test_fail("Zero area validation", f"Expected 400, got {response.status_code}")
    except Exception as e:
        results.test_fail("Zero area validation", str(e))

def test_available_times():
    """Test available times calculation"""
    print("\n⏰ Testing Available Times API...")
    
    # Test 1: Get available times for today
    today = datetime.now().strftime('%Y-%m-%d')
    try:
        response = requests.get(f"{API_BASE}/available-times/{today}")
        if response.status_code == 200:
            data = response.json()
            if "available_times" in data and "earliest_time" in data:
                results.test_pass("Available times API structure")
                
                # Check if times are within work hours (10:00-20:00)
                valid_times = True
                for time_slot in data["available_times"]:
                    hour = int(time_slot.split(':')[0])
                    if hour < 10 or hour >= 20:
                        valid_times = False
                        break
                
                if valid_times:
                    results.test_pass("Available times within work hours")
                else:
                    results.test_fail("Available times validation", "Times outside work hours found")
            else:
                results.test_fail("Available times API structure", "Missing required fields")
        else:
            results.test_fail("Available times API", f"Status {response.status_code}")
    except Exception as e:
        results.test_fail("Available times API", str(e))
    
    # Test 2: Invalid date format
    try:
        response = requests.get(f"{API_BASE}/available-times/invalid-date")
        if response.status_code == 400:
            results.test_pass("Invalid date format validation")
        else:
            results.test_fail("Invalid date format validation", f"Expected 400, got {response.status_code}")
    except Exception as e:
        results.test_fail("Invalid date format validation", str(e))
    
    # Test 3: Future date
    future_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
    try:
        response = requests.get(f"{API_BASE}/available-times/{future_date}")
        if response.status_code == 200:
            data = response.json()
            # Future date should have more available times (no existing bookings)
            if len(data["available_times"]) > 0:
                results.test_pass("Future date available times")
            else:
                results.test_fail("Future date available times", "No available times found")
        else:
            results.test_fail("Future date available times", f"Status {response.status_code}")
    except Exception as e:
        results.test_fail("Future date available times", str(e))

def test_booking_creation():
    """Test booking creation and validation"""
    print("\n📝 Testing Booking Creation...")
    
    # Test 1: Valid booking creation
    future_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    # First get available times
    try:
        response = requests.get(f"{API_BASE}/available-times/{future_date}")
        if response.status_code == 200:
            available_times = response.json()["available_times"]
            if available_times:
                booking_data = {
                    "area_hectares": 1.5,
                    "long_grass": False,
                    "date": future_date,
                    "time": available_times[0],  # Use first available time
                    "customer_name": "Mati Kask",
                    "customer_phone": "+372 5555 1234",
                    "customer_address": "Tallinn, Estonia"
                }
                
                response = requests.post(f"{API_BASE}/bookings", json=booking_data)
                if response.status_code == 200:
                    booking = response.json()
                    
                    # Verify booking data
                    if booking["area_hectares"] == 1.5 and booking["customer_name"] == "Mati Kask":
                        results.test_pass("Valid booking creation")
                        
                        # Verify price calculation in booking
                        expected_price = 1.5 * 27.19
                        if abs(booking["final_price"] - expected_price) < 0.01:
                            results.test_pass("Booking price calculation")
                        else:
                            results.test_fail("Booking price calculation", f"Expected {expected_price}, got {booking['final_price']}")
                        
                        # Verify end time calculation
                        work_duration = 1.5 / 0.4  # 3.75 hours
                        logistics_time = 1.5
                        total_duration = work_duration + logistics_time  # 5.25 hours
                        
                        start_hour, start_min = map(int, booking["start_time"].split(':'))
                        end_hour, end_min = map(int, booking["end_time"].split(':'))
                        
                        start_minutes = start_hour * 60 + start_min
                        end_minutes = end_hour * 60 + end_min
                        actual_duration = (end_minutes - start_minutes) / 60
                        
                        if abs(actual_duration - total_duration) < 0.1:
                            results.test_pass("Booking end time calculation")
                        else:
                            results.test_fail("Booking end time calculation", f"Expected {total_duration}h, got {actual_duration}h")
                        
                        # Store booking ID for later tests
                        global test_booking_id
                        test_booking_id = booking["id"]
                        
                    else:
                        results.test_fail("Valid booking creation", "Booking data mismatch")
                else:
                    results.test_fail("Valid booking creation", f"Status {response.status_code}: {response.text}")
            else:
                results.test_fail("Valid booking creation", "No available times found")
        else:
            results.test_fail("Valid booking creation", "Could not get available times")
    except Exception as e:
        results.test_fail("Valid booking creation", str(e))
    
    # Test 2: Invalid time (outside work hours)
    try:
        booking_data = {
            "area_hectares": 1.0,
            "long_grass": False,
            "date": future_date,
            "time": "09:00",  # Before work hours
            "customer_name": "Test User",
            "customer_phone": "+372 1234 5678",
            "customer_address": "Test Address"
        }
        
        response = requests.post(f"{API_BASE}/bookings", json=booking_data)
        if response.status_code == 400:
            results.test_pass("Invalid time validation (before work hours)")
        else:
            results.test_fail("Invalid time validation", f"Expected 400, got {response.status_code}")
    except Exception as e:
        results.test_fail("Invalid time validation", str(e))
    
    # Test 3: Invalid date format
    try:
        booking_data = {
            "area_hectares": 1.0,
            "long_grass": False,
            "date": "invalid-date",
            "time": "10:00",
            "customer_name": "Test User",
            "customer_phone": "+372 1234 5678",
            "customer_address": "Test Address"
        }
        
        response = requests.post(f"{API_BASE}/bookings", json=booking_data)
        if response.status_code == 400:
            results.test_pass("Invalid date format validation")
        else:
            results.test_fail("Invalid date format validation", f"Expected 400, got {response.status_code}")
    except Exception as e:
        results.test_fail("Invalid date format validation", str(e))

def test_booking_retrieval():
    """Test booking retrieval endpoints"""
    print("\n📋 Testing Booking Retrieval...")
    
    # Test 1: Get all bookings
    try:
        response = requests.get(f"{API_BASE}/bookings")
        if response.status_code == 200:
            bookings = response.json()
            if isinstance(bookings, list):
                results.test_pass("Get all bookings API")
                
                # Check if our test booking exists
                if len(bookings) > 0:
                    results.test_pass("Bookings data retrieval")
                else:
                    results.test_fail("Bookings data retrieval", "No bookings found")
            else:
                results.test_fail("Get all bookings API", "Response is not a list")
        else:
            results.test_fail("Get all bookings API", f"Status {response.status_code}")
    except Exception as e:
        results.test_fail("Get all bookings API", str(e))
    
    # Test 2: Get bookings by date
    future_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    try:
        response = requests.get(f"{API_BASE}/bookings/{future_date}")
        if response.status_code == 200:
            bookings = response.json()
            if isinstance(bookings, list):
                results.test_pass("Get bookings by date API")
            else:
                results.test_fail("Get bookings by date API", "Response is not a list")
        else:
            results.test_fail("Get bookings by date API", f"Status {response.status_code}")
    except Exception as e:
        results.test_fail("Get bookings by date API", str(e))
    
    # Test 3: Invalid date format for date-specific endpoint
    try:
        response = requests.get(f"{API_BASE}/bookings/invalid-date")
        if response.status_code == 400:
            results.test_pass("Invalid date format validation (bookings by date)")
        else:
            results.test_fail("Invalid date format validation (bookings by date)", f"Expected 400, got {response.status_code}")
    except Exception as e:
        results.test_fail("Invalid date format validation (bookings by date)", str(e))

def test_scheduling_algorithm():
    """Test complex scheduling scenarios"""
    print("\n🧠 Testing Scheduling Algorithm...")
    
    future_date = (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')
    
    # Test 1: Create multiple bookings and verify time slot blocking
    try:
        # Get initial available times
        response = requests.get(f"{API_BASE}/available-times/{future_date}")
        if response.status_code == 200:
            initial_times = response.json()["available_times"]
            initial_count = len(initial_times)
            
            if initial_count > 0:
                # Create first booking
                booking1_data = {
                    "area_hectares": 2.0,  # 5 hours work + 1.5 logistics = 6.5 hours total
                    "long_grass": False,
                    "date": future_date,
                    "time": initial_times[0],
                    "customer_name": "Jaan Tamm",
                    "customer_phone": "+372 5555 2345",
                    "customer_address": "Tartu, Estonia"
                }
                
                response1 = requests.post(f"{API_BASE}/bookings", json=booking1_data)
                if response1.status_code == 200:
                    # Get available times after first booking
                    response = requests.get(f"{API_BASE}/available-times/{future_date}")
                    if response.status_code == 200:
                        after_first_times = response.json()["available_times"]
                        
                        # Should have fewer available times
                        if len(after_first_times) < initial_count:
                            results.test_pass("Time slot blocking after booking")
                            
                            # Verify the booked time is no longer available
                            if initial_times[0] not in after_first_times:
                                results.test_pass("Booked time slot removed from available times")
                            else:
                                results.test_fail("Booked time slot removal", "Booked time still available")
                        else:
                            results.test_fail("Time slot blocking", "Available times not reduced after booking")
                    else:
                        results.test_fail("Time slot blocking test", "Could not get updated available times")
                else:
                    results.test_fail("Scheduling algorithm test", f"First booking failed: {response1.status_code}")
            else:
                results.test_fail("Scheduling algorithm test", "No initial available times")
        else:
            results.test_fail("Scheduling algorithm test", "Could not get initial available times")
    except Exception as e:
        results.test_fail("Scheduling algorithm test", str(e))
    
    # Test 2: Large area booking (should take most of the day)
    try:
        large_area_date = (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')
        
        # Get available times for large booking
        response = requests.get(f"{API_BASE}/available-times/{large_area_date}")
        if response.status_code == 200:
            available_times = response.json()["available_times"]
            
            if available_times:
                # Book large area (4 hectares = 10 hours work + 1.5 logistics = 11.5 hours)
                large_booking_data = {
                    "area_hectares": 4.0,
                    "long_grass": True,
                    "date": large_area_date,
                    "time": "10:00",  # Start early
                    "customer_name": "Peeter Saar",
                    "customer_phone": "+372 5555 3456",
                    "customer_address": "Pärnu, Estonia"
                }
                
                response = requests.post(f"{API_BASE}/bookings", json=large_booking_data)
                if response.status_code == 200:
                    booking = response.json()
                    
                    # Verify end time calculation for large booking
                    end_time = booking["end_time"]
                    end_hour = int(end_time.split(':')[0])
                    
                    # Should end around 21:30 (10:00 + 11.5 hours)
                    if end_hour >= 21:
                        results.test_pass("Large area booking end time calculation")
                        
                        # Check if this blocks most of the day
                        response = requests.get(f"{API_BASE}/available-times/{large_area_date}")
                        if response.status_code == 200:
                            remaining_times = response.json()["available_times"]
                            
                            # Should have very few or no available times left
                            if len(remaining_times) < 3:  # Allow some flexibility
                                results.test_pass("Large booking blocks most of day")
                            else:
                                results.test_fail("Large booking day blocking", f"Still {len(remaining_times)} times available")
                        else:
                            results.test_fail("Large booking day blocking test", "Could not check remaining times")
                    else:
                        results.test_fail("Large area booking end time", f"Expected end after 21:00, got {end_time}")
                else:
                    results.test_fail("Large area booking creation", f"Status {response.status_code}")
            else:
                results.test_fail("Large area booking test", "No available times found")
        else:
            results.test_fail("Large area booking test", "Could not get available times")
    except Exception as e:
        results.test_fail("Large area booking test", str(e))

def test_business_logic_validation():
    """Test specific business logic requirements"""
    print("\n💼 Testing Business Logic Validation...")
    
    # Test 1: Verify work duration formula (area / 0.4)
    test_areas = [0.5, 1.0, 2.5, 4.0]
    for area in test_areas:
        try:
            response = requests.post(f"{API_BASE}/calculate-price", params={
                "area_hectares": area,
                "long_grass": False
            })
            if response.status_code == 200:
                data = response.json()
                expected_duration = area / 0.4
                
                if abs(data["work_duration_hours"] - expected_duration) < 0.01:
                    results.test_pass(f"Work duration formula validation ({area} hectares)")
                else:
                    results.test_fail(f"Work duration formula ({area} hectares)", 
                                    f"Expected {expected_duration}, got {data['work_duration_hours']}")
            else:
                results.test_fail(f"Work duration test ({area} hectares)", f"API error: {response.status_code}")
        except Exception as e:
            results.test_fail(f"Work duration test ({area} hectares)", str(e))
    
    # Test 2: Verify base price formula (27.19€ per hectare)
    test_areas = [0.5, 1.0, 2.0, 3.5]
    for area in test_areas:
        try:
            response = requests.post(f"{API_BASE}/calculate-price", params={
                "area_hectares": area,
                "long_grass": False
            })
            if response.status_code == 200:
                data = response.json()
                expected_base_price = area * 27.19
                
                if abs(data["base_price"] - expected_base_price) < 0.01:
                    results.test_pass(f"Base price formula validation ({area} hectares)")
                else:
                    results.test_fail(f"Base price formula ({area} hectares)", 
                                    f"Expected {expected_base_price}, got {data['base_price']}")
            else:
                results.test_fail(f"Base price test ({area} hectares)", f"API error: {response.status_code}")
        except Exception as e:
            results.test_fail(f"Base price test ({area} hectares)", str(e))
    
    # Test 3: Verify long grass premium (25% extra)
    try:
        area = 2.0
        response = requests.post(f"{API_BASE}/calculate-price", params={
            "area_hectares": area,
            "long_grass": True
        })
        if response.status_code == 200:
            data = response.json()
            base_price = area * 27.19
            expected_premium = base_price * 0.25
            expected_final = base_price + expected_premium
            
            if abs(data["long_grass_premium"] - expected_premium) < 0.01:
                results.test_pass("Long grass premium calculation (25%)")
            else:
                results.test_fail("Long grass premium calculation", 
                                f"Expected {expected_premium}, got {data['long_grass_premium']}")
            
            if abs(data["final_price"] - expected_final) < 0.01:
                results.test_pass("Final price with long grass premium")
            else:
                results.test_fail("Final price with long grass premium", 
                                f"Expected {expected_final}, got {data['final_price']}")
        else:
            results.test_fail("Long grass premium test", f"API error: {response.status_code}")
    except Exception as e:
        results.test_fail("Long grass premium test", str(e))

def main():
    """Run all tests"""
    print("🚀 Starting Estonian Lawn Mowing Backend Tests")
    print(f"Backend URL: {API_BASE}")
    print("="*60)
    
    # Run all test suites
    test_price_calculation()
    test_available_times()
    test_booking_creation()
    test_booking_retrieval()
    test_scheduling_algorithm()
    test_business_logic_validation()
    
    # Print final results
    success = results.summary()
    
    if success:
        print("\n🎉 All tests passed! Backend is working correctly.")
        return 0
    else:
        print(f"\n⚠️  {results.failed} tests failed. Backend needs attention.")
        return 1

if __name__ == "__main__":
    sys.exit(main())