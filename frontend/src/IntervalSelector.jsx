import "./IntervalSelector.css"

function IntervalSelector({ value, onChange, intervalTypes}) {
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