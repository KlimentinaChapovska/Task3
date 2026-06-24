import { useState, type KeyboardEvent } from "react";
import { useWeather } from "../hooks/useWeather";

export function WeatherLookup() {
  const [city, setCity] = useState("");
  const { status, data, errorMsg, fetchWeather } = useWeather();

  function handleKeyDown(e: KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter") fetchWeather(city);
  }

  return (
    <section aria-labelledby="weather-heading">
      <h2 id="weather-heading">City Temperature</h2>

      <div className="input-row">
        <label htmlFor="city-input" className="sr-only">
          City name
        </label>
        <input
          id="city-input"
          type="text"
          value={city}
          onChange={(e) => setCity(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Enter a city, e.g. London"
          disabled={status === "loading"}
          className="text-input"
          aria-label="City name"
        />
        <button
          onClick={() => fetchWeather(city)}
          disabled={status === "loading"}
          className="primary-btn"
          aria-label="Get temperature"
        >
          {status === "loading" ? "Loading…" : "Get Temperature"}
        </button>
      </div>

      {status === "loading" && (
        <p className="status-msg" role="status" aria-live="polite">
          Fetching weather…
        </p>
      )}

      {status === "error" && (
        <p className="error-msg" role="alert">
          {errorMsg}
        </p>
      )}

      {status === "success" && data && (
        <div className="weather-card" aria-live="polite">
          <div className="weather-city">
            {data.city}
            {data.country ? `, ${data.country}` : ""}
          </div>
          <div className="weather-temp">
            {data.temperature}
            {data.unit}
          </div>
          {data.condition && (
            <div className="weather-condition">{data.condition}</div>
          )}
        </div>
      )}
    </section>
  );
}
