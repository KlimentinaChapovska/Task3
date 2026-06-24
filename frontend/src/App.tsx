import { DiceRoller } from "./components/DiceRoller";
import { WeatherLookup } from "./components/WeatherLookup";
import "./App.css";

export default function App() {
  return (
    <main className="app-container">
      <header className="app-header">
        <h1>MADA Demo</h1>
        <p className="app-subtitle">React + FastAPI · Deployment Showcase</p>
      </header>

      <div className="features-grid">
        <div className="card">
          <DiceRoller />
        </div>
        <div className="card">
          <WeatherLookup />
        </div>
      </div>
    </main>
  );
}
