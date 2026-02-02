const status = document.getElementById("status");

function render(state) {
  status.textContent = state.active ? "AKTIV 🔴" : "INAKTIV ⚪";
}

document.body.addEventListener("click", () => {
  fetch("/toggle", { method: "POST" });
});

const ws = new WebSocket(`ws://${location.host}/ws`);

ws.onmessage = (event) => {
  const state = JSON.parse(event.data);
  render(state);
};