import { useEffect, useState } from "react";

function App() {
  const [data, setData] = useState({
    temp: 0,
    humi: 0,
    light: 0
  });

  // 🔄 Fetch sensor data mỗi 2s
  useEffect(() => {
    const interval = setInterval(() => {
      fetch("http://localhost:5000/data")
        .then(res => res.json())
        .then(setData);
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  // 🎮 Điều khiển thiết bị
  const control = (device, state) => {
    fetch("http://localhost:5000/control", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ device, state })
    });
  };

  return (
    <div style={{ padding: 20 }}>
      <h1>IoT Dashboard</h1>

      <h2>🌡 Temperature: {data.temp}°C</h2>
      <h2>💧 Humidity: {data.humi}%</h2>
      <h2>💡 Light: {data.light}%</h2>

      <hr />

      <h2>Controls</h2>

      <button onClick={() => control("fan", true)}>Fan ON</button>
      <button onClick={() => control("fan", false)}>Fan OFF</button>

      <br /><br />

      <button onClick={() => control("led", true)}>LED ON</button>
      <button onClick={() => control("led", false)}>LED OFF</button>
    </div>
  );
}

export default App;