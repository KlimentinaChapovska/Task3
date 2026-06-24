export interface WeatherData {
  city: string;
  country: string;
  latitude: number;
  longitude: number;
  temperature: number;
  unit: string;
  condition: string | null;
}

export interface ApiError {
  detail: string;
}
