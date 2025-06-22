import { useEffect, useState } from "react";
const API_URL = import.meta.env.VITE_BACKEND_API_URL;
import "./Predictions.css"
import IntervalSelector from "./IntervalSelector";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

const intervalTypes = ["7", "14", "30"];

const getDateNDaysAgoInclusive = (n) => {
  const d = new Date();
  d.setDate(d.getDate() + (n - 1)); //Include first and last day
  return d.toISOString().slice(0, 10);
};

function Predictions({fuelType}) {
  const [data, setData] = useState(null);
  const end = new Date().toISOString().slice(0, 10);
  const [interval, setInterval] = useState("7");
  const [start, setStart] = useState(getDateNDaysAgoInclusive(interval));

  useEffect(() => {
    setStart(getDateNDaysAgoInclusive(interval));
  }, [interval]);

  useEffect(() => {
    fetch(`${API_URL}/api/average_price_daily/?fuel_type=${fuelType}&start_date=${end}&end_date=${start}`)
      .then(res => res.json())
      .then(json => {
        setData(json ?? "N/A");
        console.log("Fetched data:", json);
        console.log("Start date:", start);
        console.log("End date:", end);
    });

  }, [fuelType, start]);
  

  const yMin = data && data.length
    ? Math.floor(Math.min(...data.map(d => d.avg_price)) / 5) * 5
    : 0;

  const yMax = data && data.length
    ? Math.ceil(Math.max(...data.map(d => d.avg_price)) / 5) * 5
    : 100;

    return (
    <div className="home-bg">
        <IntervalSelector value={interval} onChange={setInterval} intervalTypes={intervalTypes}/>
        <h2 className="graph-title">Predicted Price Range ({fuelType})</h2>
      <div className="predictions-chart-container" data-testid="predictions-chart-container">
        <ResponsiveContainer>
          <LineChart data={data}>
            <XAxis dataKey="date" />
            <YAxis dataKey="avg_price" domain={[yMin, yMax]}/>
            <Tooltip
            followCursor={true}
              formatter={(value) => [`${value.toFixed(2)}`, 'Average Price']}
              labelFormatter={(label) => `Date: ${label}`}
            />
            <Line type="monotone" dataKey="avg_price" stroke="#222" dot />
          </LineChart>
        </ResponsiveContainer>
        </div>
    </div>
    );
}

export default Predictions;