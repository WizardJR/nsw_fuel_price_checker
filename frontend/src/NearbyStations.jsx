import { useEffect, useState } from "react";
import "./NearbyStations.css";

const API_URL = import.meta.env.VITE_BACKEND_API_URL;

export default function NearbyStations({ fuelType }) {
  const [postcode, setPostcode] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch stations for postcode
  const fetchData = async () => {
    setLoading(true);
    setError(null);

    try {
      const res = await fetch(
        `${API_URL}/api/nearby_stations/?fuel_type=${fuelType}&postcode=${postcode}`
      );
      const data = await res.json();

      if (data.error) {
        setError(data.error);
        setResults([]);
      } else {
        setResults(data);
      }
    } catch {
      setError("Failed to load stations");
    }

    setLoading(false);
  };

  // Autofetch on fuel type change
  useEffect(() => {
    fetchData();
  }, [fuelType]);

  return (
    <div className="home-bg-dark">
    <div className="stations-container">

      {loading && <div className="stations-loading">Loading…</div>}
      {error && <div className="stations-error">{error}</div>}

      {/* Results */}
      <ul className="stations-list">
        {results.map((s) => (
          <li key={s.station_code} className="station-item">
            <div className="station-left">
              <div className="station-name">{s.name}</div>
              <div className="station-name">{s.station_name}</div>
              <div className="station-address">{s.address}</div>
            </div>

            <div className="station-right">
              <div className="station-price">
                {s.price ? Number(s.price).toFixed(1) : "N/A"}
              </div>
            </div>
          </li>
        ))}
      </ul>
      <div className="postcode-search">
        <input
          type="text"
          value={postcode}
          onChange={(e) => setPostcode(e.target.value)}
          placeholder="Enter postcode"
          className="postcode-input"
        />
        <button onClick={fetchData} className="postcode-btn">
          Search
        </button>
      </div>
    </div>
    </div>
  );
}