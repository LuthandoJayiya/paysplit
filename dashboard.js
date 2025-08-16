// ===================== DASHBOARD FUNCTIONALITY =====================
// Keeps track of transactions and calculates summary stats

// Sample transactions array (in real app, fetch from API/backend)
let transactions = [];

// Function to add a transaction
function addTransaction(amount, recipients) {
  const date = new Date().toLocaleString();
  const splitDetails = recipients.map((p, i) => `R${((amount * p)/100).toFixed(2)} (${p}%)`).join(", ");

  const transaction = {
    amount,
    recipients,
    splitDetails,
    date
  };

  transactions.push(transaction);
  updateDashboard();
}

// Function to update dashboard stats and table
function updateDashboard() {
  // Update stats
  document.getElementById("totalTransactions").textContent = transactions.length;
  const allRecipients = transactions.reduce((acc, t) => acc + t.recipients.length, 0);
  document.getElementById("totalRecipients").textContent = allRecipients;
  const totalAmount = transactions.reduce((acc, t) => acc + t.amount, 0);
  document.getElementById("totalAmount").textContent = `R${totalAmount.toFixed(2)}`;

  // Update table
  const tbody = document.querySelector("#transactionsTable tbody");
  tbody.innerHTML = "";
  transactions.forEach((t, i) => {
    const row = `<tr>
      <td>${i + 1}</td>
      <td>R${t.amount.toFixed(2)}</td>
      <td>${t.recipients.join(", ")}</td>
      <td>${t.splitDetails}</td>
      <td>${t.date}</td>
    </tr>`;
    tbody.innerHTML += row;
  });
}

// ===================== SAMPLE DATA =====================
addTransaction(1000, [50, 30, 20]);
addTransaction(500, [60, 40]);
addTransaction(2000, [70, 20, 10]);
