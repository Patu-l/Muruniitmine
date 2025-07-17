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
  const [bookedSlots, setBookedSlots] = useState([]);
  const [priceCalculation, setPriceCalculation] = useState(null);
  const [customerName, setCustomerName] = useState("");
  const [customerPhone, setCustomerPhone] = useState("");
  const [customerAddress, setCustomerAddress] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [showFAQ, setShowFAQ] = useState(false);

  // Calculate price when area or long grass changes
  useEffect(() => {
    if (area && parseFloat(area) > 0) {
      calculatePrice();
    }
  }, [area, longGrass]);

  // Get available times when date or area changes
  useEffect(() => {
    if (selectedDate && area && parseFloat(area) > 0) {
      getAvailableTimes();
    }
  }, [selectedDate, area]);

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
      const response = await axios.get(`${API}/available-times/${selectedDate}`, {
        params: {
          area_hectares: parseFloat(area)
        }
      });
      setAvailableTimes(response.data.available_times);
      setBookedSlots(response.data.booked_slots);
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
      
      setMessage(`Broneering edukalt tehtud! Töö ID: ${response.data.id}`);
      
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
      setBookedSlots([]);
      
    } catch (error) {
      console.error("Error creating booking:", error);
      setMessage(`Viga broneeringu tegemisel: ${error.response?.data?.detail || error.message}`);
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

  const getNextWorkingDay = () => {
    const today = new Date();
    let nextDay = new Date(today);
    
    // Find next working day (Monday = 1, Friday = 5)
    do {
      nextDay.setDate(nextDay.getDate() + 1);
    } while (nextDay.getDay() === 0 || nextDay.getDay() === 6); // Skip Saturday and Sunday
    
    return nextDay.toISOString().split('T')[0];
  };

  const isWorkingDay = (date) => {
    const day = new Date(date).getDay();
    return day >= 1 && day <= 5; // Monday to Friday
  };

  const faqData = [
    {
      question: "Millal te töötate?",
      answer: "Töötame esmaspäevast reedeni kell 8:00-18:00. Nädalavahetustel me ei tööta."
    },
    {
      question: "Kas pakute garantiid?",
      answer: "Jah, pakume 100% rahulolu garantiid. Kui te pole meie tööga rahul, tuleme tagasi ja teeme uuesti tasuta."
    },
    {
      question: "Miks mõned ajad pole saadaval?",
      answer: "Meie süsteem näitab ainult vabad aegu. Iga töö vahel lisame 1,5 tundi logistikaega, et jõuda järgmise kliendi juurde."
    },
    {
      question: "Kuidas toimub broneeringu tühistamine?",
      answer: "24 tundi enne planeeritud tööd saate tühistada tasuta. Hilisema tühistamise korral tagastame 50% broneeringu summast."
    },
    {
      question: "Kas töötate ka vihma korral?",
      answer: "Vihma korral lükkame töö edasi järgmisele sobivale tööpäevale. Võtame teiega ühendust ilmaolude muutudes."
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-green-100">
      {/* Hero Section */}
      <div className="relative bg-gradient-to-r from-green-600 to-green-700 text-white py-20">
        <div className="absolute inset-0 bg-black opacity-50"></div>
        <div 
          className="absolute inset-0 bg-cover bg-center"
          style={{
            backgroundImage: "url('https://images.unsplash.com/photo-1558904541-efa843a96f01')",
            backgroundBlendMode: 'multiply'
          }}
        ></div>
        <div className="relative container mx-auto px-4 text-center">
          <div className="bg-black bg-opacity-30 backdrop-blur-sm rounded-2xl p-8 max-w-4xl mx-auto">
            <h1 className="text-5xl font-bold mb-4 text-shadow-lg">
              Muruniitmine
            </h1>
            <p className="text-xl mb-8 text-shadow-md">
              Kvaliteetne muruniitmisteenus kogu Eestis<br />
              Broneeri kiiresti ja mugavalt!
            </p>
            <div className="flex flex-wrap justify-center gap-4">
              <div className="bg-white bg-opacity-20 backdrop-blur-sm rounded-lg p-4 min-w-32">
                <div className="text-2xl font-bold">E-R</div>
                <div className="text-sm">8:00-18:00</div>
              </div>
              <div className="bg-white bg-opacity-20 backdrop-blur-sm rounded-lg p-4 min-w-32">
                <div className="text-2xl font-bold">27,19€</div>
                <div className="text-sm">Hektari eest</div>
              </div>
              <div className="bg-white bg-opacity-20 backdrop-blur-sm rounded-lg p-4 min-w-32">
                <div className="text-2xl font-bold">Kohe</div>
                <div className="text-sm">Broneering</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {/* Service Features */}
          <div className="grid md:grid-cols-3 gap-6 mb-8">
            <div className="bg-white rounded-xl shadow-lg p-6 text-center">
              <div 
                className="w-full h-48 bg-cover bg-center rounded-lg mb-4"
                style={{
                  backgroundImage: "url('https://images.unsplash.com/photo-1458245201577-fc8a130b8829')"
                }}
              ></div>
              <h3 className="text-xl font-semibold text-green-800 mb-2">Professionaalne Tehnika</h3>
              <p className="text-gray-600">Kasutame kvaliteetset ja hästi hooldatud muruniitmistehnikat</p>
            </div>
            
            <div className="bg-white rounded-xl shadow-lg p-6 text-center">
              <div 
                className="w-full h-48 bg-cover bg-center rounded-lg mb-4"
                style={{
                  backgroundImage: "url('https://images.unsplash.com/photo-1501520158826-76df880863a3')"
                }}
              ></div>
              <h3 className="text-xl font-semibold text-green-800 mb-2">Kiire Teenindus</h3>
              <p className="text-gray-600">Efektiivsed töövõtted ja punktuaalne teenindus</p>
            </div>
            
            <div className="bg-white rounded-xl shadow-lg p-6 text-center">
              <div 
                className="w-full h-48 bg-cover bg-center rounded-lg mb-4"
                style={{
                  backgroundImage: "url('https://images.unsplash.com/photo-1558904541-efa843a96f01')"
                }}
              ></div>
              <h3 className="text-xl font-semibold text-green-800 mb-2">Garantiitud Kvaliteet</h3>
              <p className="text-gray-600">100% rahulolu garantii ja kliendile orienteeritud lähenemine</p>
            </div>
          </div>

          {/* Main Form */}
          <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
            <h2 className="text-2xl font-bold text-green-800 mb-6 text-center">
              Broneeri Muruniitmine
            </h2>
            
            <form onSubmit={handleBooking} className="space-y-6">
              {/* Area Input */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Niidetav pindala (hektarit) *
                </label>
                <input
                  type="number"
                  step="0.1"
                  min="0.1"
                  value={area}
                  onChange={(e) => setArea(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                  placeholder="Näiteks: 1.5"
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
                  Pikk rohi <span className="text-gray-500">(üle 17cm, lisab 25% hinda)</span>
                </label>
              </div>

              {/* Price Calculation Display - Enhanced */}
              {priceCalculation && (
                <div className="bg-gradient-to-r from-green-50 to-blue-50 border border-green-200 rounded-xl p-6 shadow-sm">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-bold text-green-800 flex items-center">
                      <span className="mr-2">💰</span> Hinnakalkulatsioon
                    </h3>
                    <div className="text-2xl font-bold text-green-600">
                      {formatPrice(priceCalculation.final_price)}
                    </div>
                  </div>
                  
                  <div className="grid md:grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <div className="flex justify-between items-center py-2 border-b border-gray-200">
                        <span className="text-gray-600">Pindala:</span>
                        <span className="font-medium">{priceCalculation.area_hectares} ha</span>
                      </div>
                      <div className="flex justify-between items-center py-2 border-b border-gray-200">
                        <span className="text-gray-600">Põhihind:</span>
                        <span className="font-medium">{formatPrice(priceCalculation.base_price)}</span>
                      </div>
                      {priceCalculation.long_grass_premium > 0 && (
                        <div className="flex justify-between items-center py-2 border-b border-gray-200">
                          <span className="text-gray-600">Pika rohi lisatasu:</span>
                          <span className="font-medium text-orange-600">+{formatPrice(priceCalculation.long_grass_premium)}</span>
                        </div>
                      )}
                    </div>
                    
                    <div className="space-y-2">
                      <div className="flex justify-between items-center py-2 border-b border-gray-200">
                        <span className="text-gray-600">Töö kestus:</span>
                        <span className="font-medium">{priceCalculation.work_duration_hours.toFixed(1)} h</span>
                      </div>
                      <div className="flex justify-between items-center py-2 border-b border-gray-200">
                        <span className="text-gray-600">Tööhind/ha:</span>
                        <span className="font-medium">27,19€</span>
                      </div>
                      <div className="flex justify-between items-center py-2 text-lg font-bold text-green-800">
                        <span>Kokku:</span>
                        <span>{formatPrice(priceCalculation.final_price)}</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Date Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Kuupäev * <span className="text-gray-500">(töötame E-R)</span>
                </label>
                <input
                  type="date"
                  value={selectedDate}
                  min={getTodayDate()}
                  onChange={(e) => {
                    if (isWorkingDay(e.target.value)) {
                      setSelectedDate(e.target.value);
                    } else {
                      setMessage("⚠️ Töötame ainult esmaspäevast reedeni!");
                    }
                  }}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                />
                {selectedDate && !isWorkingDay(selectedDate) && (
                  <p className="text-red-600 text-sm mt-1">⚠️ Valitud kuupäev pole tööpäev. Palun valige E-R.</p>
                )}
              </div>

              {/* Time Selection and Booking Overview - Professional Calendar */}
              {selectedDate && area && isWorkingDay(selectedDate) && (
                <div className="space-y-6">
                  <div className="border-t pt-6">
                    <h3 className="text-lg font-semibold text-gray-800 mb-4">Aja valik</h3>
                    
                    {loading ? (
                      <div className="text-center py-8">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-500 mx-auto"></div>
                        <p className="mt-3 text-gray-600">Laadin saadaolevaid aegu...</p>
                      </div>
                    ) : (
                      <div className="space-y-6">
                        {/* Date Overview */}
                        <div className="bg-slate-50 border border-slate-200 rounded-lg p-4">
                          <div className="flex items-center justify-between mb-2">
                            <h4 className="font-medium text-slate-800">
                              {new Date(selectedDate).toLocaleDateString('et-EE', { 
                                weekday: 'long', 
                                year: 'numeric', 
                                month: 'long', 
                                day: 'numeric' 
                              })}
                            </h4>
                            <span className="text-sm text-slate-600">
                              Töö kestus: {priceCalculation?.work_duration_hours.toFixed(1)}h
                            </span>
                          </div>
                          <div className="flex flex-wrap gap-4 text-sm text-slate-600">
                            <span className="flex items-center">
                              <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
                              {availableTimes.length} vaba aega
                            </span>
                            <span className="flex items-center">
                              <div className="w-3 h-3 bg-red-500 rounded-full mr-2"></div>
                              {bookedSlots.length} broneeritud
                            </span>
                            <span className="flex items-center">
                              <div className="w-3 h-3 bg-blue-500 rounded-full mr-2"></div>
                              {area}ha pindala
                            </span>
                          </div>
                        </div>

                        {/* Professional Time Grid */}
                        <div className="border border-gray-200 rounded-lg overflow-hidden">
                          <div className="bg-gray-50 px-4 py-3 border-b">
                            <h4 className="font-medium text-gray-800">Tööpäeva ajakava (8:00 - 18:00)</h4>
                          </div>
                          
                          <div className="p-4">
                            {/* Time slots grid */}
                            <div className="grid grid-cols-6 gap-2 mb-4">
                              {/* Generate time slots from 8:00 to 18:00 */}
                              {Array.from({ length: 20 }, (_, i) => {
                                const hour = Math.floor(i / 2) + 8;
                                const minute = (i % 2) * 30;
                                const timeSlot = `${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`;
                                
                                // Check if this time slot is available
                                const isAvailable = availableTimes.includes(timeSlot);
                                const isBooked = bookedSlots.some(slot => 
                                  timeSlot >= slot.start_time && timeSlot < slot.end_time
                                );
                                const isSelected = selectedTime === timeSlot;
                                
                                let bgColor = 'bg-gray-100';
                                let textColor = 'text-gray-400';
                                let cursor = 'cursor-not-allowed';
                                
                                if (isBooked) {
                                  bgColor = 'bg-red-100 border-red-200';
                                  textColor = 'text-red-700';
                                } else if (isAvailable) {
                                  bgColor = 'bg-green-100 hover:bg-green-200 border-green-200';
                                  textColor = 'text-green-700';
                                  cursor = 'cursor-pointer';
                                  
                                  if (isSelected) {
                                    bgColor = 'bg-green-600 border-green-600';
                                    textColor = 'text-white';
                                  }
                                }
                                
                                return (
                                  <button
                                    key={timeSlot}
                                    type="button"
                                    disabled={!isAvailable}
                                    onClick={() => isAvailable && setSelectedTime(timeSlot)}
                                    className={`
                                      ${bgColor} ${textColor} ${cursor}
                                      p-2 rounded-md text-sm font-medium border transition-all
                                      ${isAvailable ? 'hover:shadow-sm' : ''}
                                    `}
                                  >
                                    {timeSlot}
                                  </button>
                                );
                              })}
                            </div>
                            
                            {/* Legend */}
                            <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600 pt-3 border-t">
                              <div className="flex items-center">
                                <div className="w-3 h-3 bg-green-100 border border-green-200 rounded mr-2"></div>
                                <span>Saadaval</span>
                              </div>
                              <div className="flex items-center">
                                <div className="w-3 h-3 bg-red-100 border border-red-200 rounded mr-2"></div>
                                <span>Broneeritud</span>
                              </div>
                              <div className="flex items-center">
                                <div className="w-3 h-3 bg-gray-100 border border-gray-200 rounded mr-2"></div>
                                <span>Pole tööaeg</span>
                              </div>
                              <div className="flex items-center">
                                <div className="w-3 h-3 bg-green-600 rounded mr-2"></div>
                                <span>Valitud</span>
                              </div>
                            </div>
                          </div>
                        </div>

                        {/* Booked Slots Details */}
                        {bookedSlots.length > 0 && (
                          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                            <h4 className="font-medium text-red-800 mb-3">Broneeritud ajad sellel päeval</h4>
                            <div className="space-y-2">
                              {bookedSlots.map((slot, index) => (
                                <div key={index} className="flex items-center justify-between p-3 bg-white rounded-md border">
                                  <div className="flex items-center">
                                    <div className="w-2 h-2 bg-red-500 rounded-full mr-3"></div>
                                    <span className="font-medium text-gray-800">
                                      {slot.start_time} - {slot.end_time}
                                    </span>
                                  </div>
                                  <div className="text-sm text-gray-600">
                                    {slot.area_hectares}ha • {slot.customer_name}
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                        
                        {/* Selected Time Confirmation */}
                        {selectedTime && (
                          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                            <div className="flex items-center">
                              <div className="w-3 h-3 bg-green-600 rounded-full mr-3"></div>
                              <div>
                                <p className="font-medium text-green-800">
                                  Valitud aeg: {selectedTime}
                                </p>
                                <p className="text-sm text-green-600">
                                  Töö kestab umbes {priceCalculation?.work_duration_hours.toFixed(1)} tundi
                                </p>
                              </div>
                            </div>
                          </div>
                        )}
                        
                        {/* No available times message */}
                        {availableTimes.length === 0 && (
                          <div className="text-center py-8 text-red-600 bg-red-50 border border-red-200 rounded-lg">
                            <p className="font-medium">Valitud kuupäevaks pole sobilikke aegu</p>
                            <p className="text-sm mt-2">Palun valige teine kuupäev või vähendage pindala suurust</p>
                            <p className="text-sm text-gray-600 mt-1">
                              Järgmine vaba tööpäev: {getNextWorkingDay()}
                            </p>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Customer Information */}
              <div className="border-t pt-6">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">Kontaktandmed</h3>
                
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Nimi *
                    </label>
                    <input
                      type="text"
                      value={customerName}
                      onChange={(e) => setCustomerName(e.target.value)}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                      placeholder="Teie nimi"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Telefon *
                    </label>
                    <input
                      type="tel"
                      value={customerPhone}
                      onChange={(e) => setCustomerPhone(e.target.value)}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                      placeholder="+372 5XXX XXXX"
                    />
                  </div>
                </div>

                <div className="mt-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Töö aadress *
                  </label>
                  <textarea
                    value={customerAddress}
                    onChange={(e) => setCustomerAddress(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500"
                    rows="2"
                    placeholder="Töö toimumise aadress"
                  />
                </div>
              </div>

              {/* Submit Button */}
              <button
                type="submit"
                disabled={loading || !selectedTime}
                className={`w-full py-4 px-6 rounded-lg font-semibold text-white transition-colors ${
                  loading || !selectedTime
                    ? "bg-gray-400 cursor-not-allowed"
                    : "bg-green-600 hover:bg-green-700 focus:ring-2 focus:ring-green-500"
                }`}
              >
                {loading ? (
                  <div className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                    Broneerin...
                  </div>
                ) : (
                  "Broneeri Muruniitmine"
                )}
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

          {/* FAQ Section */}
          <div className="bg-white rounded-xl shadow-lg p-8">
            <h3 className="text-2xl font-bold text-gray-800 mb-6 text-center">
              ❓ Korduma Kippuvad Küsimused
            </h3>
            <div className="space-y-4">
              {faqData.map((faq, index) => (
                <div key={index} className="border border-gray-200 rounded-lg">
                  <button
                    onClick={() => setShowFAQ(showFAQ === index ? null : index)}
                    className="w-full px-6 py-4 text-left flex justify-between items-center hover:bg-gray-50 transition-colors"
                  >
                    <span className="font-medium text-gray-800">{faq.question}</span>
                    <span className="text-green-600 text-xl">
                      {showFAQ === index ? "−" : "+"}
                    </span>
                  </button>
                  {showFAQ === index && (
                    <div className="px-6 pb-4 text-gray-600">
                      {faq.answer}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;