import "./FuelTypeSelector.css";

const fuelTypes = ["DL", "E10", "P95", "P98", "U91", "PDL", "LPG"];

function FuelTypeSelector({ value, onChange }) {
  return (
    <div className="fuel-type-tiles">
      {fuelTypes.map(ft => (
        <button
          key={ft}
          className={`fuel-tile${value === ft ? " active" : ""}`}
          onClick={() => onChange(ft)}
          type="button"
        >
          {ft}
        </button>
      ))}
    </div>
  );
}

export default FuelTypeSelector;