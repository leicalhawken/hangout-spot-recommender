// Add more input fields for more friends
document.getElementById("add-friend").addEventListener("click", () => {
  const newInput = document.createElement("input");
  newInput.type = "text";
  newInput.name = "location";
  newInput.placeholder = "Enter location for another friend";
  newInput.required = true;
  document.getElementById("locations").appendChild(newInput);
});

// Handle form submit
document.getElementById("location-form").addEventListener("submit", async (e) => {
  e.preventDefault();

  const form = e.target;
  const locations = Array.from(form.querySelectorAll('input[name="location"]')).map(input => input.value);
  const category = document.getElementById("category").value;

  const response = await fetch("/recommend", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ locations, category })
  });

  const data = await response.json();
  displayResults(data);
});

function displayResults(data) {
  const resultsDiv = document.getElementById("results");
  resultsDiv.innerHTML = "<h3>Recommended Spots:</h3>";
  data.forEach((spot) => {
  resultsDiv.innerHTML += `<p><strong>${spot.name}</strong> - ${spot.address}</p>`;
  });
}
