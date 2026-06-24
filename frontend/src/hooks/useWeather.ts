import { useState } from "react";
import type { WeatherData } from "../types/weather";

type Status = "idle" | "loading" | "success" | "error";

export function useWeather() {
  const [status, setStatus] = useState<Status>("idle");
  const [data, setData] = useState<WeatherData | null>(null);
  const [errorMsg, setErrorMsg] = useState<string>("");

  async function fetchWeather(city: string) {
    const trimmed = city.trim();
    if (!trimmed) {
      setErrorMsg("Please enter a city name.");
      setStatus("error");
      return;
    }

    setStatus("loading");
    setData(null);
    setErrorMsg("");

    try {
      const res = await fetch(
        `/api/weather?city=${encodeURIComponent(trimmed)}`
      );
      const json = await res.json();

      if (!res.ok) {
        setErrorMsg(json.detail ?? "An unexpected error occurred.");
        setStatus("error");
        return;
      }

      setData(json as WeatherData);
      setStatus("success");
    } catch {
      setErrorMsg("Could not reach the server. Check your connection.");
      setStatus("error");
    }
  }

  return { status, data, errorMsg, fetchWeather };
}
