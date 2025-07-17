#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Estonian Lawn Mowing Booking System
Tests all endpoints with realistic Estonian data
"""

import requests
import json
import uuid
from datetime import datetime, timedelta
import sys

# Backend URL from environment
BACKEND_URL = "https://2c6a3726-d442-468e-b237-1ec54a61b59c.preview.emergentagent.com/api"

class BackendTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.test_results = []
        self.created_providers = []
        self.created_bookings = []
        self.created_assignments = []
        
    def log_test(self, test_name, success, details="", response_data=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        if response_data and not success:
            print(f"   Response: {response_data}")
        print()
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "response": response_data
        })
    
    def test_health_check(self):
        """Test basic API health"""
        try:
            response = requests.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                if "Estonian Lawn Mowing API" in data.get("message", ""):
                    self.log_test("Health Check", True, "API is running")
                    return True
                else:
                    self.log_test("Health Check", False, "Unexpected response message", data)
                    return False
            else:
                self.log_test("Health Check", False, f"Status code: {response.status_code}", response.text)
                return False
        except Exception as e:
            self.log_test("Health Check", False, f"Connection error: {str(e)}")
            return False
    
    def test_price_calculation(self):
        """Test price calculation endpoint"""
        try:
            # Test normal pricing
            response = requests.post(f"{self.base_url}/calculate-price", 
                                   params={"area_hectares": 2.5, "long_grass": False})
            
            if response.status_code == 200:
                data = response.json()
                expected_base = 2.5 * 27.19  # 67.975
                expected_duration = 2.5 / 0.4  # 6.25 hours
                
                if (abs(data["base_price"] - expected_base) < 0.01 and 
                    abs(data["work_duration_hours"] - expected_duration) < 0.01 and
                    data["long_grass_premium"] == 0):
                    self.log_test("Price Calculation - Normal", True, f"2.5ha = {data['final_price']}€")
                else:
                    self.log_test("Price Calculation - Normal", False, "Incorrect calculations", data)
            else:
                self.log_test("Price Calculation - Normal", False, f"Status: {response.status_code}", response.text)
            
            # Test long grass premium
            response = requests.post(f"{self.base_url}/calculate-price", 
                                   params={"area_hectares": 1.0, "long_grass": True})
            
            if response.status_code == 200:
                data = response.json()
                base_price = 27.19
                premium = base_price * 0.25
                expected_final = base_price + premium
                
                if abs(data["final_price"] - expected_final) < 0.01:
                    self.log_test("Price Calculation - Long Grass", True, f"1ha with premium = {data['final_price']}€")
                else:
                    self.log_test("Price Calculation - Long Grass", False, "Incorrect premium calculation", data)
            else:
                self.log_test("Price Calculation - Long Grass", False, f"Status: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("Price Calculation", False, f"Error: {str(e)}")
    
    def test_available_times(self):
        """Test available times endpoint"""
        try:
            # Test for a working day (Monday)
            test_date = "2024-12-16"  # Monday
            response = requests.get(f"{self.base_url}/available-times/{test_date}", 
                                  params={"area_hectares": 1.0})
            
            if response.status_code == 200:
                data = response.json()
                if (data["date"] == test_date and 
                    isinstance(data["available_times"], list) and
                    len(data["available_times"]) > 0):
                    self.log_test("Available Times - Working Day", True, 
                                f"Found {len(data['available_times'])} slots")
                else:
                    self.log_test("Available Times - Working Day", False, "No available times", data)
            else:
                self.log_test("Available Times - Working Day", False, f"Status: {response.status_code}", response.text)
            
            # Test for weekend (should be empty)
            weekend_date = "2024-12-14"  # Saturday
            response = requests.get(f"{self.base_url}/available-times/{weekend_date}")
            
            if response.status_code == 200:
                data = response.json()
                if len(data["available_times"]) == 0:
                    self.log_test("Available Times - Weekend", True, "No slots on weekend")
                else:
                    self.log_test("Available Times - Weekend", False, "Should not have weekend slots", data)
            else:
                self.log_test("Available Times - Weekend", False, f"Status: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("Available Times", False, f"Error: {str(e)}")
    
    def test_booking_creation(self):
        """Test booking creation"""
        try:
            # First check available times to get a valid slot
            test_date = "2024-12-19"  # Thursday
            response = requests.get(f"{self.base_url}/available-times/{test_date}", 
                                  params={"area_hectares": 1.5})
            
            available_time = "08:00"  # Default fallback
            if response.status_code == 200:
                data = response.json()
                if data["available_times"]:
                    available_time = data["available_times"][0]
            
            booking_data = {
                "area_hectares": 1.5,
                "long_grass": False,
                "date": test_date,
                "time": available_time,
                "customer_name": "Mart Tamm",
                "customer_phone": "+372 5123 4567",
                "customer_address": "Tallinna tn 15, Tartu"
            }
            
            response = requests.post(f"{self.base_url}/bookings", json=booking_data)
            
            if response.status_code == 200:
                data = response.json()
                if (data["customer_name"] == booking_data["customer_name"] and
                    data["date"] == booking_data["date"] and
                    data["start_time"] == booking_data["time"]):
                    self.log_test("Booking Creation", True, f"Booking created for {data['customer_name']}")
                    self.created_bookings.append(data["id"])
                    return data["id"]
                else:
                    self.log_test("Booking Creation", False, "Data mismatch", data)
            else:
                self.log_test("Booking Creation", False, f"Status: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("Booking Creation", False, f"Error: {str(e)}")
        return None
    
    def test_get_bookings(self):
        """Test getting bookings"""
        try:
            # Get all bookings
            response = requests.get(f"{self.base_url}/bookings")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Get All Bookings", True, f"Retrieved {len(data)} bookings")
            else:
                self.log_test("Get All Bookings", False, f"Status: {response.status_code}", response.text)
            
            # Get bookings by date
            test_date = "2024-12-19"
            response = requests.get(f"{self.base_url}/bookings/{test_date}")
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Get Bookings by Date", True, f"Found {len(data)} bookings for {test_date}")
            else:
                self.log_test("Get Bookings by Date", False, f"Status: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("Get Bookings", False, f"Error: {str(e)}")
    
    def test_service_provider_management(self):
        """Test service provider CRUD operations"""
        try:
            # Create service provider
            provider_data = {
                "name": "Peeter Kask",
                "phone": "+372 5234 5678",
                "email": "peeter.kask@email.ee",
                "specialization": "large_areas",
                "hourly_rate": 25.0,
                "max_area_per_day": 15.0,
                "working_days": [0, 1, 2, 3, 4],
                "start_time": "08:00",
                "end_time": "17:00",
                "is_active": True
            }
            
            response = requests.post(f"{self.base_url}/providers", json=provider_data)
            
            if response.status_code == 200:
                data = response.json()
                provider_id = data["id"]
                self.created_providers.append(provider_id)
                self.log_test("Create Service Provider", True, f"Created provider: {data['name']}")
                
                # Test get all providers
                response = requests.get(f"{self.base_url}/providers")
                if response.status_code == 200:
                    providers = response.json()
                    self.log_test("Get All Providers", True, f"Retrieved {len(providers)} providers")
                else:
                    self.log_test("Get All Providers", False, f"Status: {response.status_code}")
                
                # Test get specific provider
                response = requests.get(f"{self.base_url}/providers/{provider_id}")
                if response.status_code == 200:
                    provider = response.json()
                    self.log_test("Get Specific Provider", True, f"Retrieved {provider['name']}")
                else:
                    self.log_test("Get Specific Provider", False, f"Status: {response.status_code}")
                
                # Test update provider
                update_data = provider_data.copy()
                update_data["hourly_rate"] = 30.0
                response = requests.put(f"{self.base_url}/providers/{provider_id}", json=update_data)
                if response.status_code == 200:
                    updated = response.json()
                    if updated["hourly_rate"] == 30.0:
                        self.log_test("Update Provider", True, "Hourly rate updated to 30€")
                    else:
                        self.log_test("Update Provider", False, "Rate not updated", updated)
                else:
                    self.log_test("Update Provider", False, f"Status: {response.status_code}")
                
                return provider_id
            else:
                self.log_test("Create Service Provider", False, f"Status: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("Service Provider Management", False, f"Error: {str(e)}")
        return None
    
    def test_work_assignments(self, booking_id=None, provider_id=None):
        """Test work assignment system"""
        if not booking_id or not provider_id:
            self.log_test("Work Assignments", False, "Missing booking_id or provider_id")
            return
        
        try:
            # Create work assignment
            assignment_data = {
                "booking_id": booking_id,
                "provider_id": provider_id,
                "scheduled_date": "2024-12-19",
                "scheduled_time": "08:00",
                "estimated_duration": 3.75,
                "special_instructions": "Tähelepanu: kitsas värav, kasutada väikest masinat"
            }
            
            response = requests.post(f"{self.base_url}/assignments", json=assignment_data)
            
            if response.status_code == 200:
                data = response.json()
                assignment_id = data["id"]
                self.created_assignments.append(assignment_id)
                self.log_test("Create Work Assignment", True, f"Assignment created: {assignment_id}")
                
                # Test get all assignments
                response = requests.get(f"{self.base_url}/assignments")
                if response.status_code == 200:
                    assignments = response.json()
                    self.log_test("Get All Assignments", True, f"Retrieved {len(assignments)} assignments")
                else:
                    self.log_test("Get All Assignments", False, f"Status: {response.status_code}")
                
                # Test get assignments by provider
                response = requests.get(f"{self.base_url}/assignments/provider/{provider_id}")
                if response.status_code == 200:
                    provider_assignments = response.json()
                    self.log_test("Get Provider Assignments", True, f"Found {len(provider_assignments)} assignments")
                else:
                    self.log_test("Get Provider Assignments", False, f"Status: {response.status_code}")
                
                # Test update assignment status
                response = requests.put(f"{self.base_url}/assignments/{assignment_id}/status", 
                                      params={"status": "in_progress"})
                if response.status_code == 200:
                    self.log_test("Update Assignment Status", True, "Status updated to in_progress")
                else:
                    self.log_test("Update Assignment Status", False, f"Status: {response.status_code}")
                
                # Test complete assignment with rating
                response = requests.put(f"{self.base_url}/assignments/{assignment_id}/status", 
                                      params={"status": "completed", "rating": 4.8, "feedback": "Suurepärane töö!"})
                if response.status_code == 200:
                    self.log_test("Complete Assignment", True, "Assignment completed with rating")
                else:
                    self.log_test("Complete Assignment", False, f"Status: {response.status_code}")
                
            else:
                self.log_test("Create Work Assignment", False, f"Status: {response.status_code}", response.text)
                
        except Exception as e:
            self.log_test("Work Assignments", False, f"Error: {str(e)}")
    
    def test_analytics_endpoints(self):
        """Test analytics and reporting endpoints"""
        try:
            # Test dashboard analytics
            response = requests.get(f"{self.base_url}/analytics/dashboard")
            if response.status_code == 200:
                data = response.json()
                required_fields = ["total_bookings", "total_revenue", "this_month_bookings", 
                                 "active_providers", "upcoming_assignments", "completed_this_month"]
                if all(field in data for field in required_fields):
                    self.log_test("Dashboard Analytics", True, 
                                f"Total bookings: {data['total_bookings']}, Revenue: {data['total_revenue']}€")
                else:
                    self.log_test("Dashboard Analytics", False, "Missing required fields", data)
            else:
                self.log_test("Dashboard Analytics", False, f"Status: {response.status_code}")
            
            # Test monthly revenue
            response = requests.get(f"{self.base_url}/analytics/monthly-revenue")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Monthly Revenue", True, f"Retrieved {len(data)} months of data")
            else:
                self.log_test("Monthly Revenue", False, f"Status: {response.status_code}")
            
            # Test provider performance
            response = requests.get(f"{self.base_url}/analytics/provider-performance")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Provider Performance", True, f"Performance data for {len(data)} providers")
            else:
                self.log_test("Provider Performance", False, f"Status: {response.status_code}")
            
            # Test booking trends
            response = requests.get(f"{self.base_url}/analytics/booking-trends")
            if response.status_code == 200:
                data = response.json()
                if "day_trends" in data and "time_trends" in data:
                    self.log_test("Booking Trends", True, "Day and time trends retrieved")
                else:
                    self.log_test("Booking Trends", False, "Missing trend data", data)
            else:
                self.log_test("Booking Trends", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Analytics Endpoints", False, f"Error: {str(e)}")
    
    def test_notification_system(self):
        """Test reminder and notification system"""
        try:
            # Test get upcoming reminders
            response = requests.get(f"{self.base_url}/reminders/upcoming")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Get Upcoming Reminders", True, f"Found {len(data)} upcoming reminders")
            else:
                self.log_test("Get Upcoming Reminders", False, f"Status: {response.status_code}")
            
            # Test send reminder notifications
            response = requests.post(f"{self.base_url}/reminders/send")
            if response.status_code == 200:
                data = response.json()
                self.log_test("Send Reminders", True, f"Sent {data['notifications_sent']} notifications")
            else:
                self.log_test("Send Reminders", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Notification System", False, f"Error: {str(e)}")
    
    def test_error_handling(self):
        """Test error handling and validation"""
        try:
            # Test invalid date format
            response = requests.get(f"{self.base_url}/available-times/invalid-date")
            if response.status_code == 400:
                self.log_test("Error Handling - Invalid Date", True, "Correctly rejected invalid date")
            else:
                self.log_test("Error Handling - Invalid Date", False, f"Status: {response.status_code}")
            
            # Test negative area
            response = requests.post(f"{self.base_url}/calculate-price", 
                                   params={"area_hectares": -1.0})
            if response.status_code == 400:
                self.log_test("Error Handling - Negative Area", True, "Correctly rejected negative area")
            else:
                self.log_test("Error Handling - Negative Area", False, f"Status: {response.status_code}")
            
            # Test non-existent provider
            response = requests.get(f"{self.base_url}/providers/non-existent-id")
            if response.status_code == 404:
                self.log_test("Error Handling - Non-existent Provider", True, "Correctly returned 404")
            else:
                self.log_test("Error Handling - Non-existent Provider", False, f"Status: {response.status_code}")
                
        except Exception as e:
            self.log_test("Error Handling", False, f"Error: {str(e)}")
    
    def cleanup_test_data(self):
        """Clean up test data"""
        try:
            # Delete test providers
            for provider_id in self.created_providers:
                response = requests.delete(f"{self.base_url}/providers/{provider_id}")
                if response.status_code == 200:
                    print(f"✅ Cleaned up provider: {provider_id}")
                else:
                    print(f"❌ Failed to clean up provider: {provider_id}")
            
            print(f"\n🧹 Cleanup completed. Deleted {len(self.created_providers)} providers")
            
        except Exception as e:
            print(f"❌ Cleanup error: {str(e)}")
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Estonian Lawn Mowing Backend API Tests")
        print("=" * 60)
        
        # Basic connectivity
        if not self.test_health_check():
            print("❌ Health check failed. Stopping tests.")
            return
        
        # Original booking system tests
        print("\n📋 Testing Original Booking System")
        print("-" * 40)
        self.test_price_calculation()
        self.test_available_times()
        booking_id = self.test_booking_creation()
        self.test_get_bookings()
        
        # Service provider management
        print("\n👷 Testing Service Provider Management")
        print("-" * 40)
        provider_id = self.test_service_provider_management()
        
        # Work assignment system (only if we have both booking and provider)
        print("\n📝 Testing Work Assignment System")
        print("-" * 40)
        if booking_id and provider_id:
            self.test_work_assignments(booking_id, provider_id)
        else:
            self.log_test("Work Assignments", False, "Missing booking_id or provider_id for testing")
        
        # Analytics and reporting
        print("\n📊 Testing Analytics and Reporting")
        print("-" * 40)
        self.test_analytics_endpoints()
        
        # Notification system
        print("\n🔔 Testing Notification System")
        print("-" * 40)
        self.test_notification_system()
        
        # Error handling
        print("\n⚠️  Testing Error Handling")
        print("-" * 40)
        self.test_error_handling()
        
        # Summary
        print("\n📈 Test Summary")
        print("=" * 60)
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print(f"\n❌ Failed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   - {result['test']}: {result['details']}")
        
        # Cleanup
        print(f"\n🧹 Cleaning up test data...")
        self.cleanup_test_data()
        
        return passed_tests, failed_tests

if __name__ == "__main__":
    tester = BackendTester()
    passed, failed = tester.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if failed == 0 else 1)