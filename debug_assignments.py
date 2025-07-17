#!/usr/bin/env python3
"""
Debug test for work assignments
"""

import requests
import json

BACKEND_URL = "https://2c6a3726-d442-468e-b237-1ec54a61b59c.preview.emergentagent.com/api"

def debug_assignments():
    # First create a booking
    booking_data = {
        "area_hectares": 1.5,
        "long_grass": False,
        "date": "2024-12-18",  # Tomorrow
        "time": "10:00",
        "customer_name": "Test Customer",
        "customer_phone": "+372 5123 4567",
        "customer_address": "Test Address"
    }
    
    print("Creating booking...")
    response = requests.post(f"{BACKEND_URL}/bookings", json=booking_data)
    if response.status_code == 200:
        booking = response.json()
        booking_id = booking["id"]
        print(f"✅ Booking created: {booking_id}")
    else:
        print(f"❌ Booking failed: {response.status_code} - {response.text}")
        return
    
    # Create a provider
    provider_data = {
        "name": "Test Provider",
        "phone": "+372 5234 5678",
        "email": "test@email.ee",
        "specialization": "general",
        "hourly_rate": 25.0,
        "max_area_per_day": 10.0,
        "working_days": [0, 1, 2, 3, 4],
        "start_time": "08:00",
        "end_time": "17:00",
        "is_active": True
    }
    
    print("Creating provider...")
    response = requests.post(f"{BACKEND_URL}/providers", json=provider_data)
    if response.status_code == 200:
        provider = response.json()
        provider_id = provider["id"]
        print(f"✅ Provider created: {provider_id}")
    else:
        print(f"❌ Provider failed: {response.status_code} - {response.text}")
        return
    
    # Now create assignment
    assignment_data = {
        "booking_id": booking_id,
        "provider_id": provider_id,
        "scheduled_date": "2024-12-18",
        "scheduled_time": "10:00",
        "estimated_duration": 3.75,
        "special_instructions": "Test assignment"
    }
    
    print("Creating assignment...")
    response = requests.post(f"{BACKEND_URL}/assignments", json=assignment_data)
    if response.status_code == 200:
        assignment = response.json()
        print(f"✅ Assignment created: {assignment['id']}")
        
        # Test other assignment endpoints
        print("Testing get all assignments...")
        response = requests.get(f"{BACKEND_URL}/assignments")
        if response.status_code == 200:
            assignments = response.json()
            print(f"✅ Retrieved {len(assignments)} assignments")
        else:
            print(f"❌ Get assignments failed: {response.status_code}")
        
        # Test get by provider
        print("Testing get assignments by provider...")
        response = requests.get(f"{BACKEND_URL}/assignments/provider/{provider_id}")
        if response.status_code == 200:
            provider_assignments = response.json()
            print(f"✅ Retrieved {len(provider_assignments)} provider assignments")
        else:
            print(f"❌ Get provider assignments failed: {response.status_code}")
        
        # Test status update
        print("Testing status update...")
        response = requests.put(f"{BACKEND_URL}/assignments/{assignment['id']}/status", 
                              params={"status": "completed", "rating": 4.5})
        if response.status_code == 200:
            print("✅ Status updated successfully")
        else:
            print(f"❌ Status update failed: {response.status_code} - {response.text}")
        
        # Cleanup
        print("Cleaning up...")
        requests.delete(f"{BACKEND_URL}/providers/{provider_id}")
        print("✅ Cleanup completed")
        
    else:
        print(f"❌ Assignment failed: {response.status_code} - {response.text}")
        # Cleanup provider
        requests.delete(f"{BACKEND_URL}/providers/{provider_id}")

if __name__ == "__main__":
    debug_assignments()