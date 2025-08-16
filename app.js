// ===================== DEMO PAYMENT SPLITTER =====================
// Splits a customer payment across multiple recipients based on percentages

document.getElementById("splitForm").addEventListener("submit", function(e) {
  e.preventDefault(); // Prevent page reload

  const amount = parseFloat(document.getElementById("amount").value);
  const recipients = document.getElementById("recipients").value
    .split(",")
    .map(Number);

  // Validate percentages sum to 100
  const totalPercent = recipients.reduce((a, b) => a + b, 0);
  if (totalPercent !== 100) {
    document.getElementById("results").innerHTML =
      "<p class='text-danger'>Error: Percentages must add up to 100%</p>";
    return;
  }

  // Generate result display
  let resultsHTML = "<h4>Split Results:</h4><ul class='list-group'>";
  recipients.forEach((percent, i) => {
    const share = (amount * percent) / 100;
    resultsHTML += `<li class='list-group-item'>Recipient ${i+1}: R${share.toFixed(2)} (${percent}%)</li>`;
  });
  resultsHTML += "</ul>";

  document.getElementById("results").innerHTML = resultsHTML;
});
