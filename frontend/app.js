// All requests use relative URLs; nginx proxies /api/ and /health to the backend.

const $ = (id) => document.getElementById(id);

function esc(value) {
  return String(value).replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  })[c]);
}

async function getJson(url, options) {
  const res = await fetch(url, options);
  const body = await res.json().catch(() => null);
  if (!res.ok) {
    const err = new Error(`HTTP ${res.status}`);
    err.status = res.status;
    err.body = body;
    throw err;
  }
  return body;
}

async function loadHealth() {
  const badge = $("health");
  try {
    const h = await getJson("/health");
    badge.textContent = `Backend ${h.status} · v${h.version}`;
    badge.className = "badge badge-ok";
  } catch (e) {
    badge.textContent = "Backend unreachable";
    badge.className = "badge badge-down";
  }
}

async function loadPayments() {
  const box = $("payments");
  try {
    const payments = await getJson("/api/payments");
    const counts = { COMPLETED: 0, PENDING: 0, FAILED: 0 };
    payments.forEach((p) => { counts[p.status] = (counts[p.status] || 0) + 1; });
    $("stat-total").textContent = payments.length;
    $("stat-completed").textContent = counts.COMPLETED;
    $("stat-pending").textContent = counts.PENDING;
    $("stat-failed").textContent = counts.FAILED;

    if (payments.length === 0) {
      box.className = "state";
      box.textContent = "No payments yet.";
      return;
    }
    const rows = payments
      .slice()
      .sort((a, b) => b.id - a.id)
      .map((p) => `<tr>
        <td>#${esc(p.id)}</td><td>${esc(p.payer)}</td><td>${esc(p.payee)}</td>
        <td class="num">${esc(p.amount.toFixed(2))} ${esc(p.currency)}</td>
        <td><span class="status status-${esc(p.status.toLowerCase())}">${esc(p.status)}</span></td>
        <td>${esc(new Date(p.created_at).toLocaleString())}</td></tr>`)
      .join("");
    box.className = "table-wrap";
    box.innerHTML = `<table><thead><tr><th>ID</th><th>Payer</th><th>Payee</th>
      <th class="num">Amount</th><th>Status</th><th>Created</th></tr></thead><tbody>${rows}</tbody></table>`;
  } catch (e) {
    box.className = "state state-error";
    box.textContent = `Could not load payments (${e.message}).`;
  }
}

async function loadNotifications() {
  const box = $("notifications");
  try {
    const notes = await getJson("/api/notifications");
    if (notes.length === 0) {
      box.className = "state";
      box.textContent = "No notifications yet.";
      return;
    }
    box.className = "";
    box.innerHTML = `<ul class="notes">${notes
      .map((n) => `<li><span>${esc(n.message)}</span><time>${esc(new Date(n.created_at).toLocaleTimeString())}</time></li>`)
      .join("")}</ul>`;
  } catch (e) {
    box.className = "state state-error";
    box.textContent = `Could not load notifications (${e.message}).`;
  }
}

function describeError(e) {
  if (e.status === 422 && e.body && Array.isArray(e.body.detail)) {
    return e.body.detail.map((d) => `${d.loc[d.loc.length - 1]}: ${d.msg}`).join("; ");
  }
  return (e.body && e.body.detail) || e.message;
}

$("payment-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  const msg = $("form-msg");
  const button = form.querySelector("button");
  const data = Object.fromEntries(new FormData(form));
  const payload = { ...data, amount: Number(data.amount) };

  button.disabled = true;
  msg.className = "form-msg";
  msg.textContent = "Sending…";
  try {
    const created = await getJson("/api/payments", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    msg.className = "form-msg ok";
    msg.textContent = `Payment #${created.id} created.`;
    form.reset();
    await Promise.all([loadPayments(), loadNotifications()]);
  } catch (e) {
    msg.className = "form-msg error";
    msg.textContent = `Rejected: ${describeError(e)}`;
  } finally {
    button.disabled = false;
  }
});

loadHealth();
loadPayments();
loadNotifications();
setInterval(loadHealth, 15000);
