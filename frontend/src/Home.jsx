import { useEffect, useState } from "react";
const API_URL = import.meta.env.VITE_BACKEND_API_URL;
import "./Home.css"

function Home({fuelType}) {
  const [avg, setAvg] = useState(null);

  useEffect(() => {
    const today = new Date().toISOString().slice(0, 10);
    fetch(`${API_URL}/api/average_price_daily/?fuel_type=${fuelType}&start_date=${today}&end_date=${today}`)
      .then(res => res.json())
      .then(data => {
        setAvg(data[0]?.avg_price ?? "N/A");
    });
  }, [fuelType]);
  
  function formatAvgPrice(avg) {
    if (avg === "N/A" || avg === null || avg === undefined) return "N/A";
    return Number(avg).toFixed(2);
  }

    return (
    <div className="home-bg">
        <div className="center-content">
        <h2>Today's Average Fuel Price ({fuelType})</h2>
        <div className="avg-price">{formatAvgPrice(avg)}</div>
        </div>
    </div>
    );
}

export default Home;