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

  const faqData = [
    {
      question: "Millal te töötate?",
      answer: "Töötame esmaspäevast pühapäevani kell 8:00-18:00. Viimane broneering sõltub teie pindala suurusest - suurema pindala korral tuleb varem broneerida."
    },
    {
      question: "Kuidas hinda arvutatakse?",
      answer: "Põhihind on 27,19€ hektari kohta. Pika rohi korral lisandub 25% lisatasu. Töö kestus arvutatakse nii: tunnid = pindala ÷ 0,4"
    },
    {
      question: "Miks mõned ajad pole saadaval?",
      answer: "Meie süsteem näitab ainult vabad aegu. Iga töö vahel lisame 1,5 tundi logistikaega, et jõuda järgmise kliendi juurde."
    },
    {
      question: "Kas võin tühistada broneeringu?",
      answer: "Jah, võite helistada meile vähemalt 24 tundi enne planeeritud tööd. Kontaktandmed saadetakse teile kinnituskiri."
    },
    {
      question: "Kas töötate ka vihma korral?",
      answer: "Vihma korral lükkame töö edasi järgmisele sobivale päevale. Võtame teiega ühendust ilmaolude muutudes."
    }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-green-100">
      {/* Hero Section */}
      <div className="relative bg-gradient-to-r from-green-600 to-green-700 text-white py-20">
        <div className="absolute inset-0 bg-black opacity-20"></div>
        <div 
          className="absolute inset-0 bg-cover bg-center"
          style={{
            backgroundImage: "url('https://images.unsplash.com/photo-1558904541-efa843a96f01')",
            backgroundBlendMode: 'multiply'
          }}
        ></div>
        <div className="relative container mx-auto px-4 text-center">
          <h1 className="text-5xl font-bold mb-4">
            🌿 Professionaalne Muruniitmine
          </h1>
          <p className="text-xl mb-8 max-w-2xl mx-auto">
            Kvaliteetne muruniitmisteenus kogu Eestis. Broneeri kiiresti ja mugavalt!
          </p>
          <div className="flex justify-center space-x-4">
            <div className="bg-white bg-opacity-20 backdrop-blur-sm rounded-lg p-4">
              <div className="text-2xl font-bold">8:00-18:00</div>
              <div className="text-sm">Tööaeg</div>
            </div>
            <div className="bg-white bg-opacity-20 backdrop-blur-sm rounded-lg p-4">
              <div className="text-2xl font-bold">27,19€</div>
              <div className="text-sm">Hektari eest</div>
            </div>
            <div className="bg-white bg-opacity-20 backdrop-blur-sm rounded-lg p-4">
              <div className="text-2xl font-bold">Kohe</div>
              <div className="text-sm">Broneering</div>
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
              <h3 className="text-xl font-semibold text-green-800 mb-2">🚜 Professionaalne Tehnika</h3>
              <p className="text-gray-600">Kasutame kvaliteetset ja hästi hooldatud muruniitmistehnikat</p>
            </div>
            
            <div className="bg-white rounded-xl shadow-lg p-6 text-center">
              <div 
                className="w-full h-48 bg-cover bg-center rounded-lg mb-4"
                style={{
                  backgroundImage: "url('https://images.unsplash.com/photo-1501520158826-76df880863a3')"
                }}
              ></div>
              <h3 className="text-xl font-semibold text-green-800 mb-2">⚡ Kiire Teenindus</h3>
              <p className="text-gray-600">Efektiivsed töövõtted ja punktuaalne teenindus</p>
            </div>
            
            <div className="bg-white rounded-xl shadow-lg p-6 text-center">
              <div 
                className="w-full h-48 bg-cover bg-center rounded-lg mb-4"
                style={{
                  backgroundImage: "url('https://images.unsplash.com/photo-1558904541-efa843a96f01')"
                }}
              ></div>
              <h3 className="text-xl font-semibold text-green-800 mb-2">✅ Garantiitud Kvaliteet</h3>
              <p className="text-gray-600">Kõrgeim kvaliteet ja kliendile orienteeritud lähenemine</p>
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
                  Pikk rohi (lisab 25% hinda)
                </label>
              </div>

              {/* Price Calculation Display */}
              {priceCalculation && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-6">
                  <h3 className="font-semibold text-green-800 mb-3 flex items-center">
                    💰 Hinnakalkulatsioon
                  </h3>
                  <div className="grid md:grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="font-medium">Koguhind: <span className="text-green-600 text-lg">{formatPrice(priceCalculation.final_price)}</span></p>
                      <p>Töö kestus: <span className="font-medium">{priceCalculation.work_duration_hours.toFixed(1)} tundi</span></p>
                    </div>
                    <div>
                      <p>Põhihind: {formatPrice(priceCalculation.base_price)}</p>
                      {priceCalculation.long_grass_premium > 0 && (
                        <p>Pika rohi lisatasu: {formatPrice(priceCalculation.long_grass_premium)}</p>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* Date Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Kuupäev *
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
              {selectedDate && area && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Kellaaeg *
                  </label>
                  {loading ? (
                    <div className="text-center py-6">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-500 mx-auto"></div>
                      <p className="mt-2 text-gray-600">Laadin saadaolevaid aegu...</p>
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
                    <div className="text-center py-6 text-red-600 bg-red-50 rounded-lg">
                      <p className="font-medium">⚠️ Valitud kuupäevaks pole sobilikke aegu</p>
                      <p className="text-sm mt-1">Palun valige teine kuupäev või vähendage pindala suurust</p>
                    </div>
                  )}
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
                disabled={loading}
                className={`w-full py-4 px-6 rounded-lg font-semibold text-white transition-colors ${
                  loading
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
                  "🌿 Broneeri Muruniitmine"
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