export const c = (value: number) => `${value.toFixed(1)} °C`;
export const kw = (valueW: number) => `${(valueW / 1000).toFixed(1)} kW`;
export const flow = (value: number) => `${value.toFixed(2)} kg/s`;
export const pct = (value: number) => `${Math.round(value * 100)}%`;
export const speedKmh = (valueMs: number) => `${(valueMs * 3.6).toFixed(0)} km/h`;
