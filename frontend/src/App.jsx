import { useEffect, useState } from "react";
import "./App.css"
import Home from "./Home";
import History from "./History";
import Predictions from "./Predictions";
import FuelTypeSelector from "./FuelTypeSelector";
import NearbyStations from "./NearbyStations";

function App() {
  const [tab, setTab] = useState(0);
  const [fuelType, setFuelType] = useState("P95");
  useEffect(() => {
    document.title = "NSW Fuel Price Checker";
  }, []);

  return (
    <div className="app-root">
      {tab === 0 && <Home fuelType={fuelType}/>}
      {tab === 1 && <History fuelType={fuelType}/>}
      {tab === 2 && <Predictions fuelType={fuelType}/>}
      {tab === 3 && <NearbyStations fuelType={fuelType}/>}

      <FuelTypeSelector value={fuelType} onChange={setFuelType} />

      <div className="tab-list">
        <div
          className={`tab-item${tab === 0 ? " active" : ""}`}
          onClick={() => setTab(0)}
        >
          TODAY
        </div>
        <div
          className={`tab-item${tab === 1 ? " active" : ""}`}
          onClick={() => setTab(1)}
        >
          HISTORY
        </div>
        <div
          className={`tab-item${tab === 2 ? " active" : ""}`}
          onClick={() => setTab(2)}
        >
          PREDICTIONS
        </div>
        <div
          className={`tab-item${tab === 3 ? " active" : ""}`}
          onClick={() => setTab(3)}
        >
          NEARBY
        </div>
      </div>
    </div>
  );
}

export default App;