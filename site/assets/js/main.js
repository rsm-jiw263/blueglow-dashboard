// Main JavaScript for BlueGlow Helper

// API Server URL
const API_BASE_URL = "http://localhost:5001";

document.addEventListener("DOMContentLoaded", function () {
  console.log("BlueGlow Helper loaded");

  // Set date selector default value to today
  const today = new Date().toISOString().split("T")[0];
  document.getElementById("start-date").value = today;

  // Load best week by default
  loadForecast();
});

async function loadForecast() {
  try {
    // Try to load detailed forecast (3-hour timeslots)
    let response = await fetch("forecast_detailed.json");
    let data = await response.json();
    let isDetailed = true;

    if (!response.ok) {
      // If no detailed version, load standard version
      response = await fetch("forecast.json");
      data = await response.json();
      isDetailed = false;
    }

    console.log("Forecast data loaded:", data);
    console.log("Detailed mode:", isDetailed);

    // Update location and time info
    updateHeader(data, isDetailed);

    // Render forecast cards
    if (isDetailed) {
      renderDetailedForecasts(data.forecasts);
    } else {
      renderForecasts(data.forecasts);
    }
  } catch (error) {
    console.error("Failed to load forecast:", error);
    showError("Unable to load forecast data");
  }
}

function updateHeader(data, isDetailed) {
  const locationEl = document.querySelector(".info-box p");
  const timestampEl = document.querySelector(".timestamp");

  if (locationEl && data.location) {
    locationEl.textContent = `${
      data.location.name
    } (${data.location.lat.toFixed(2)}°N, ${Math.abs(data.location.lon).toFixed(
      2
    )}°W)`;
  }

  if (timestampEl && data.generated_at) {
    const date = new Date(data.generated_at);
    const formatted = date.toLocaleString("en-US", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
      timeZone: "America/Los_Angeles",
    });
    const mode = isDetailed ? "3-hour timeslots" : "Daily forecast";
    timestampEl.textContent = `Updated: ${formatted} | Mode: ${mode} | ${
      data.model_version || "v1.0"
    }`;
  }
}

function renderDetailedForecasts(forecasts) {
  const gridEl = document.querySelector(".forecast-grid");
  if (!gridEl) return;

  gridEl.innerHTML = ""; // Clear existing content

  // Sort forecasts by day of week: Monday -> Sunday
  const dayOrder = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
  ];
  const sortedForecasts = [...forecasts].sort((a, b) => {
    return dayOrder.indexOf(a.day_of_week) - dayOrder.indexOf(b.day_of_week);
  });

  sortedForecasts.forEach((forecast, index) => {
    const card = createDetailedForecastCard(forecast, index);
    gridEl.appendChild(card);
  });
}

function createDetailedForecastCard(forecast, index) {
  const card = document.createElement("div");
  card.className = "forecast-card-detailed";
  card.style.opacity = "0";
  card.style.transform = "translateY(20px)";

  // Find best timeslot (nighttime)
  const nightSlots = forecast.timeslots.filter((t) => t.is_night);
  const bestNight =
    nightSlots.length > 0
      ? nightSlots.reduce((a, b) => (a.score > b.score ? a : b))
      : forecast.timeslots[0];

  // Render 8 timeslots
  const timeslotsHTML = forecast.timeslots
    .map((slot) => {
      const isBest = slot.time === forecast.best_time;
      const isNight = slot.is_night;
      return `
            <div class="timeslot ${isBest ? "best-time" : ""} ${
        isNight ? "night-time" : "day-time"
      }">
                <div class="timeslot-time">${slot.time}</div>
                <div class="timeslot-score">
                    <span class="score-number">${slot.score}</span>
                    <span class="score-icon">${slot.icon}</span>
                </div>
                <div class="timeslot-details">
                    ${isNight ? "🌙" : "☀️"} ${
        slot.conditions.tide_level > 0 ? "⬆️" : "⬇️"
      }
                </div>
            </div>
        `;
    })
    .join("");

  card.innerHTML = `
        <div class="card-header">
            <h3>${forecast.day_of_week}</h3>
            <p class="date">${forecast.date}</p>
        </div>
        <div class="card-summary">
            <div class="score-box">
                <div class="avg-score">
                    <span class="score-value">${forecast.avg_score}</span>
                    <span class="score-label">Avg</span>
                </div>
                <div class="best-score">
                    <span class="score-value">${forecast.best_score}</span>
                    <span class="score-label">Best: ${forecast.best_time}</span>
                </div>
            </div>
        </div>
        <div class="timeslots-grid">
            ${timeslotsHTML}
        </div>
        <div class="recommendation">
            <small>💡 ${forecast.recommendation}</small>
        </div>
    `;

  // Animation effect
  setTimeout(() => {
    card.style.transition = "all 0.5s ease";
    card.style.opacity = "1";
    card.style.transform = "translateY(0)";
  }, index * 100);

  return card;
}

function renderForecasts(forecasts) {
  const gridEl = document.querySelector(".forecast-grid");
  if (!gridEl) return;

  gridEl.innerHTML = ""; // Clear existing content

  // Sort forecasts by day of week: Monday -> Sunday
  const dayOrder = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
  ];
  const sortedForecasts = [...forecasts].sort((a, b) => {
    return dayOrder.indexOf(a.day_of_week) - dayOrder.indexOf(b.day_of_week);
  });

  sortedForecasts.forEach((forecast, index) => {
    const card = createForecastCard(forecast, index);
    gridEl.appendChild(card);
  });
}

function createForecastCard(forecast, index) {
  const card = document.createElement("div");
  card.className = `forecast-card quality-${forecast.rating.toLowerCase()}`;
  card.style.opacity = "0";
  card.style.transform = "translateY(20px)";

  // Get icon for rating
  const ratingIcons = {
    Excellent: "🌟",
    Good: "✨",
    Fair: "💫",
    Poor: "⭐",
  };

  const icon = ratingIcons[forecast.rating] || "⭐";

  card.innerHTML = `
        <h3>${forecast.day_of_week}</h3>
        <p class="date">${forecast.date}</p>
        <div class="blueglow-index">
            <span class="index-value">${forecast.score}</span>
            <span class="index-label">Score ${icon}</span>
        </div>
        <p class="quality">${forecast.rating}</p>
        <div class="details">
            <p>🌙 Moon: ${forecast.conditions.moon.phase} (${(
    forecast.conditions.moon.illumination * 100
  ).toFixed(0)}%)</p>
            <p>🌊 Tide: ${
              forecast.conditions.tide.level > 0 ? "High" : "Low"
            } (${forecast.conditions.tide.level.toFixed(2)})</p>
            <p>🌊 Wave: ${forecast.conditions.wave_height_m}m</p>
            <p>🌡️ Water Temp: ${forecast.conditions.water_temp_c}°C</p>
        </div>
        <div class="recommendation">
            <small>${forecast.recommendation}</small>
        </div>
    `;

  // Animation effect
  setTimeout(() => {
    card.style.transition = "all 0.5s ease";
    card.style.opacity = "1";
    card.style.transform = "translateY(0)";
  }, index * 100);

  // Click effect
  card.addEventListener("click", function () {
    this.style.transform = "scale(1.05)";
    setTimeout(() => {
      this.style.transform = "";
    }, 200);
  });

  return card;
}

function showError(message) {
  const gridEl = document.querySelector(".forecast-grid");
  if (gridEl) {
    gridEl.innerHTML = `
            <div class="error-message" style="grid-column: 1/-1; text-align: center; padding: 2rem; color: #e74c3c;">
                <h3>❌ ${message}</h3>
                <p>Please check if forecast.json file exists</p>
            </div>
        `;
  }
}

// Query forecast from API for specified date
async function queryForecast() {
  const dateInput = document.getElementById("start-date");
  const selectedDate = dateInput.value;

  if (!selectedDate) {
    alert("Please select a date!");
    return;
  }

  const gridEl = document.querySelector(".forecast-grid");
  gridEl.innerHTML =
    '<div style="grid-column: 1/-1; text-align: center; padding: 2rem;">🔄 Querying week starting ' +
    selectedDate +
    "...</div>";

  try {
    const response = await fetch(
      `${API_BASE_URL}/api/forecast?date=${selectedDate}`
    );

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    const data = await response.json();

    if (data.success) {
      // Update subtitle with date range
      const subtitle = document.querySelector(".subtitle");
      subtitle.textContent = `${data.start_date} to ${data.end_date} | Week Avg: ${data.week_avg_score}`;

      // Update location and time info
      const locationEl = document.querySelector(".info-box p");
      const timestampEl = document.querySelector(".timestamp");

      if (locationEl && data.metadata) {
        locationEl.textContent = data.metadata.location;
      }

      if (timestampEl && data.metadata) {
        const date = new Date(data.metadata.generated_at);
        const formatted = date.toLocaleString("en-US", {
          year: "numeric",
          month: "2-digit",
          day: "2-digit",
          hour: "2-digit",
          minute: "2-digit",
        });
        timestampEl.textContent = `Query Time: ${formatted} | Mode: API Dynamic Query | ${data.metadata.model_version}`;
      }

      // Render forecast data
      renderDetailedForecasts(data.forecasts);
    } else {
      gridEl.innerHTML = `<div class="error-message" style="grid-column: 1/-1; text-align: center; padding: 2rem; color: #e74c3c;">❌ ${data.error}</div>`;
    }
  } catch (error) {
    console.error("Query failed:", error);
    gridEl.innerHTML = `
            <div class="error-message" style="grid-column: 1/-1; text-align: center; padding: 2rem; color: #e74c3c; line-height: 1.8;">
                <h3>❌ Unable to connect to API server</h3>
                <p>Please make sure API server is running:</p>
                <code style="background: rgba(0,0,0,0.2); padding: 8px; border-radius: 4px; display: inline-block; margin: 10px;">bash start_api.sh</code>
                <p><small>Error: ${error.message}</small></p>
            </div>
        `;
  }
}

// Load best week (from local JSON file)
async function loadBestWeek() {
  const dateInput = document.getElementById("start-date");
  dateInput.value = ""; // Clear date selection

  const subtitle = document.querySelector(".subtitle");
  subtitle.textContent = "7-Day Viewing Conditions - Best Week";

  // Call original load function
  await loadForecast();
}
