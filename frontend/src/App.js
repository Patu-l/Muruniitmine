import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [area, setArea] = useState("");
  const [longGrass, setLongGrass] = useState(false);
  const [selectedDate, setSelectedDate] = useState("");
  const [selectedTime, setSelectedTime] = useState("");
  const [availableTimes, setAvailableTimes] = useState([]);
  const [priceCalculation, setPriceCalculation] = useState(null);
  const [customerName, setCustomerName] = useState("");
  const [customerPhone, setCustomerPhone] = useState("");
  const [customerAddress, setCustomerAddress] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  // Calculate price when area or long grass changes
  useEffect(() => {
    if (area && parseFloat(area) > 0) {
      calculatePrice();
    }
  }, [area, longGrass]);

  // Get available times when date changes
  useEffect(() => {
    if (selectedDate) {
      getAvailableTimes();
    }
  }, [selectedDate]);

  const calculatePrice = async () => {
    try {
      const response = await axios.post(`${API}/calculate-price`, null, {
        params: {
          area_hectares: parseFloat(area),
          long_grass: longGrass
        }
      });
      setPriceCalculation(response.data);
    } catch (error) {
      console.error("Error calculating price:", error);
    }
  };

  const getAvailableTimes = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/available-times/${selectedDate}`);
      setAvailableTimes(response.data.available_times);
      setSelectedTime(""); // Reset selected time
    } catch (error) {
      console.error("Error getting available times:", error);
      setMessage("Viga saadaolevate aegade laadimisel");
    } finally {
      setLoading(false);
    }
  };

  const handleBooking = async (e) => {
    e.preventDefault();
    
    if (!area || !selectedDate || !selectedTime || !customerName || !customerPhone || !customerAddress) {
      setMessage("Palun täida kõik väljad!");
      return;
    }

    try {
      setLoading(true);
      const bookingData = {
        area_hectares: parseFloat(area),
        long_grass: longGrass,
        date: selectedDate,
        time: selectedTime,
        customer_name: customerName,
        customer_phone: customerPhone,
        customer_address: customerAddress
      };

      const response = await axios.post(`${API}/bookings`, bookingData);
      
      setMessage(`✅ Broneering edukalt tehtud! Töö ID: ${response.data.id}`);
      
      // Reset form
      setArea("");
      setLongGrass(false);
      setSelectedDate("");
      setSelectedTime("");
      setCustomerName("");
      setCustomerPhone("");
      setCustomerAddress("");
      setPriceCalculation(null);
      setAvailableTimes([]);
      
    } catch (error) {
      console.error("Error creating booking:", error);
      setMessage(`❌ Viga broneeringu tegemisel: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('et-EE', {
      style: 'currency',
      currency: 'EUR'
    }).format(price);
  };

  const getTodayDate = () => {
    const today = new Date();
    return today.toISOString().split('T')[0];
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-green-100">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-green-800 mb-2">
              🌿 Muruniitmine
            </h1>
            <p className="text-green-600 text-lg">
              Professionaalne muruniitmisteenus - Broneeri kohe!
            </p>
          </div>

          {/* Main Form */}
          <div className="bg-white rounded-xl shadow-lg p-8">
            <form onSubmit={handleBooking} className="space-y-6">
              {/* Area Input */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Niidetav pindala (hektarit)
                </label>
                <input
                  type="number"
                  step="0.1"
                  min="0.1"
                  value={area}
                  onChange={(e) => setArea(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                  placeholder="Sisesta pindala hektarites"
                />
              </div>

              {/* Long Grass Checkbox */}
              <div className="flex items-center space-x-3">
                <input
                  type="checkbox"
                  id="longGrass"
                  checked={longGrass}
                  onChange={(e) => setLongGrass(e.target.checked)}
                  className="w-5 h-5 text-green-600 border-gray-300 rounded focus:ring-green-500"
                />
                <label htmlFor="longGrass" className="text-sm font-medium text-gray-700">
                  Pikk rohi (lisab 25% hinda)
                </label>
              </div>

              {/* Price Calculation Display */}
              {priceCalculation && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <h3 className="font-semibold text-green-800 mb-2">💰 Hinnakalkulatsioon</h3>
                  <div className="space-y-1 text-sm">
                    <p><strong>Hind:</strong> {formatPrice(priceCalculation.final_price)}</p>
                    <p><strong>Töö kestus:</strong> umbes {priceCalculation.work_duration_hours.toFixed(1)} tundi</p>
                    {priceCalculation.long_grass_premium > 0 && (
                      <p><strong>Pika rohu lisatasu:</strong> {formatPrice(priceCalculation.long_grass_premium)}</p>
                    )}
                  </div>
                </div>
              )}

              {/* Date Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Kuupäev
                </label>
                <input
                  type="date"
                  value={selectedDate}
                  min={getTodayDate()}
                  onChange={(e) => setSelectedDate(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                />
              </div>

              {/* Time Selection */}
              {selectedDate && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Kellaaeg
                  </label>
                  {loading ? (
                    <div className="text-center py-4">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-500 mx-auto"></div>
                    </div>
                  ) : availableTimes.length > 0 ? (
                    <select
                      value={selectedTime}
                      onChange={(e) => setSelectedTime(e.target.value)}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                    >
                      <option value="">Vali kellaaeg</option>
                      {availableTimes.map((time) => (
                        <option key={time} value={time}>
                          {time}
                        </option>
                      ))}
                    </select>
                  ) : (
                    <div className="text-center py-4 text-red-600">
                      ⚠️ Valitud kuupäevaks pole vaba aega
                    </div>
                  )}
                </div>
              )}

              {/* Customer Information */}
              <div className="border-t pt-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">Kontaktandmed</h3>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Nimi
                    </label>
                    <input
                      type="text"
                      value={customerName}
                      onChange={(e) => setCustomerName(e.target.value)}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                      placeholder="Sisesta oma nimi"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Telefon
                    </label>
                    <input
                      type="tel"
                      value={customerPhone}
                      onChange={(e) => setCustomerPhone(e.target.value)}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                      placeholder="Sisesta telefoni number"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Aadress
                    </label>
                    <textarea
                      value={customerAddress}
                      onChange={(e) => setCustomerAddress(e.target.value)}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                      rows="3"
                      placeholder="Sisesta töö aadress"
                    />
                  </div>
                </div>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={loading}
                className={`w-full py-4 px-6 rounded-lg font-semibold text-white transition-colors ${
                  loading
                    ? "bg-gray-400 cursor-not-allowed"
                    : "bg-green-600 hover:bg-green-700 focus:ring-2 focus:ring-green-500"
                }`}
              >
                {loading ? "Broneerin..." : "🌿 Broneeri töö"}
              </button>
            </form>

            {/* Message Display */}
            {message && (
              <div className={`mt-6 p-4 rounded-lg ${
                message.includes("✅") 
                  ? "bg-green-50 border border-green-200 text-green-800"
                  : "bg-red-50 border border-red-200 text-red-800"
              }`}>
                {message}
              </div>
            )}
          </div>

          {/* Info Section */}
          <div className="mt-8 bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">ℹ️ Kuidas süsteem töötab</h3>
            <div className="space-y-2 text-sm text-gray-600">
              <p>• Tööpäev algab kell 10:00 ja lõppeb kell 20:00</p>
              <p>• Tööaeg arvutatakse: tunnid = pindala (ha) ÷ 0,4</p>
              <p>• Iga töö vahel on 1,5 tundi logistikaaega</p>
              <p>• Pikk rohi lisab 25% hinna peale</p>
              <p>• Näed ainult vaba aega vastavalt olemasolevatele broneeringutele</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;