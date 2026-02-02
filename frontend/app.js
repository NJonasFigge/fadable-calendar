// - Get the status field element
const statusField = document.getElementById("status");

// - Function to update the status field based on a given state
function updateState(state) {
  statusField.textContent = state.active ? "AKTIV 🔴" : "INAKTIV ⚪";
}

// - Establish a WebSocket connection to receive state updates
const ws = new WebSocket(`ws://${location.host}/ws`);

// - Set up WebSocket message handler to update state on receiving messages
ws.onmessage = (event) => {
  const state = JSON.parse(event.data);
  updateState(state);
};

// - Add a click event listener to the body to toggle the state
document.body.addEventListener("click", () => {
  fetch("/toggle", { method: "POST" });
});
