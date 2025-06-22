import "./IntervalSelector.css"
const intervalTypes = ["7", "14", "30", "180", "365"];

function IntervalSelector({ value, onChange }) {
  return (
    <div className="interval-type-tiles">
      {intervalTypes.map(interval => (
        <button
          key={interval}
          className={`interval-tile${value === interval ? " active" : ""}`}
          onClick={() => onChange(interval)}
          type="button"
        >
          {interval}
        </button>
      ))}
    </div>
  );
}

export default IntervalSelector;