import { useEffect, useState } from "react";
const API_URL = import.meta.env.VITE_BACKEND_API_URL;
import "./Predictions.css"
import IntervalSelector from "./IntervalSelector";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from "recharts";

const intervalTypes = ["7", "14", "30", "180", "365"];

const getDateNDaysAfterInclusive = (n) => {
  const d = new Date();
  d.setDate(d.getDate() + (n - 1));
  return d.toISOString().slice(0, 10);
};

const getDateNDaysAgoInclusive = (n) => {
  const d = new Date();
  d.setDate(d.getDate() - (n - 1));
  return d.toISOString().slice(0, 10);
};

function Predictions({fuelType}) {
  const [histData, setHistData] = useState(null);
  const [predData, setPredData] = useState(null);
  const end = new Date().toISOString().slice(0, 10);
  const [interval, setInterval] = useState("180");
  const [histStart, setHistStart] = useState(getDateNDaysAgoInclusive(interval));
  const [predEnd, setPredEnd] = useState(getDateNDaysAfterInclusive(interval));
  
    useEffect(() => {
      setHistStart(getDateNDaysAgoInclusive(interval));
    }, [interval]);

  useEffect(() => {
    setPredEnd(getDateNDaysAfterInclusive(interval));
  }, [interval]);

  useEffect(() => {
    fetch(`${API_URL}/api/average_price_daily/?fuel_type=${fuelType}&start_date=${histStart}&end_date=${end}`)
      .then(res => res.json())
      .then(json => {
        setHistData(json ?? "N/A");
    });
  }, [fuelType, histStart]);
  
  useEffect(() => {
    fetch(`${API_URL}/api/average_price_predict/?fuel_type=${fuelType}&start_date=${histStart}&end_date=${predEnd}`)
      .then(res => res.json())
      .then(json => {
        setPredData(json ?? "N/A");
    });
  }, [fuelType, predEnd]);

  const findMin = (data) => {
    if (!data || data.length === 0) return 0;
    return Math.floor(Math.min(...data.map(d => d.avg_price)) / 5) * 5;
  }

  const findMax = (data) => {
    if (!data || data.length === 0) return 200;
    return Math.ceil(Math.max(...data.map(d => d.avg_price)) / 5) * 5;
  }

  const yMin = Math.min(findMin(histData), findMin(predData));
  const yMax = Math.max(findMax(histData), findMax(predData));

  const mergedData = [];
  const mergedDataMap = new Map();

  if (histData) {
    histData.forEach(item => {
        mergedDataMap.set(item.date, { date: item.date, avg_price: item.avg_price });
    });
  }

  if (predData) {
      predData.forEach(item => {
          const existing = mergedDataMap.get(item.date) || { date: item.date };
          mergedDataMap.set(item.date, { ...existing, pred_price: item.avg_price });
      });
  }

  mergedData.push(...Array.from(mergedDataMap.values()).sort((a, b) => new Date(a.date) - new Date(b.date)));

    return (
    <div className="home-bg">
        <IntervalSelector value={interval} onChange={setInterval} intervalTypes={intervalTypes}/>
        <h2 className="graph-title">Predicted Price Range ({fuelType})</h2>
      <div className="predictions-chart-container" data-testid="predictions-chart-container">
        <ResponsiveContainer>
          <LineChart data={mergedData}>
            <XAxis dataKey="date" />
            <YAxis dataKey="avg_price" domain={[yMin, yMax]}/>
            <Tooltip
              followCursor={true}
              formatter={(value, name, props) => {
                return [`${value.toFixed(2)}`, name];
              }}
              labelFormatter={(label) => `Date: ${label}`}
            />
            <Legend />
            <Line 
              type="monotone" 
              dataKey="avg_price" 
              stroke="#222" 
              dot={false}
              name={"Historical Price"}
            />
            <Line 
              type="monotone" 
              dataKey="pred_price" 
              stroke="#FF0000"
              strokeDasharray="5 5"
              dot={false}
              name={"Predicted Price"}
            />
          </LineChart>
        </ResponsiveContainer>
        </div>
    </div>
    );
}

export default Predictions;