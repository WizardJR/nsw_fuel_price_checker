import { useEffect, useState } from "react";
const API_URL = import.meta.env.VITE_BACKEND_API_URL;
function App() {
  const [prices, setPrices] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // fetch("http://127.0.0.1:8000/api/average_price_daily/?fuel_type=E10")
    fetch(`${API_URL}/api/average_price_daily/?fuel_type=E10`)
      .then((res) => res.json())
      .then((data) => {
        setPrices(data);
        setLoading(false);
      });
  }, []);

  return (
    <div style={{ maxWidth: 600, margin: "2rem auto" }}>
      <h1>Average Fuel Prices</h1>
      {loading ? (
        <p>Loading...</p>
      ) : (
        <table border="1" cellPadding="6" style={{ width: "100%" }}>
          <thead>
            <tr>
              <th>Date</th>
              <th>Average Price</th>
            </tr>
          </thead>
          <tbody>
            {prices.map((row) => (
              <tr key={row.date}>
                <td>{row.date}</td>
                <td>{row.avg_price}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default App;