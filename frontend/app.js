const API = {
  users: "http://127.0.0.1:5001",
  events: "http://127.0.0.1:5002",
  registrations: "http://127.0.0.1:5003",
  tickets: "http://127.0.0.1:5004",
  notifications: "http://127.0.0.1:5005"
};
const $ = (s) => document.querySelector(s);
function showMessage(target, text, ok=true) {
  target.innerHTML = `<div class="result ${ok?'success':'error'}">${escapeHtml(text)}</div>`;
}
function escapeHtml(v) {
  return String(v ?? "").replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}
async function api(url, options={}) {
  const res = await fetch(url, {headers:{"Content-Type":"application/json"}, ...options});
  const data = await res.json().catch(()=>({error:"Unexpected server response"}));
  if (!res.ok) throw new Error(data.error || data.message || `Request failed (${res.status})`);
  return data;
}
let events = [];
async function loadEvents() {
  const box = $("#event-list");
  try {
    events = await api(`${API.events}/events`);
    box.innerHTML = events.length ? events.map(e => `<article class="event-card">
      <span class="tag">${Number(e.available_seats)>0 ? `${e.available_seats} SEATS LEFT` : "FULL"}</span>
      <h3>${escapeHtml(e.name)}</h3><p>${escapeHtml(e.description || "Join us for this campus event.")}</p>
      <div class="event-meta">📅 ${escapeHtml(new Date(e.event_date).toLocaleString())}<br>📍 ${escapeHtml(e.venue)}</div></article>`).join("") : '<p class="muted">No events yet. Add events through the event service API.</p>';
    $("#event-select").innerHTML = '<option value="">Choose an event</option>' + events.map(e=>`<option value="${e.id}" ${e.available_seats<=0?'disabled':''}>${escapeHtml(e.name)} (${e.available_seats} seats left)</option>`).join("");
  } catch(err) {
    box.innerHTML = `<div class="result error">Could not load events: ${escapeHtml(err.message)}. Check that all services and MySQL are running.</div>`;
  }
}
$("#user-form").addEventListener("submit", async e => {
  e.preventDefault(); const d = Object.fromEntries(new FormData(e.target));
  try {
    const user = await api(`${API.users}/users`, {method:"POST",body:JSON.stringify(d)});
    showMessage($("#message"), `Account created! Your user ID is ${user.id}. Save this ID for registration and notifications.`);
    e.target.reset(); e.target.elements.password.value = "";
    $("#registration-form").elements.user_id.value = user.id;
    $("#notification-form").elements.user_id.value = user.id;
  } catch(err) { showMessage($("#message"),err.message,false); }
});
$("#registration-form").addEventListener("submit", async e => {
  e.preventDefault(); const d=Object.fromEntries(new FormData(e.target)); d.user_id=Number(d.user_id); d.event_id=Number(d.event_id);
  try {
    const r=await api(`${API.registrations}/registrations`,{method:"POST",body:JSON.stringify(d)});
    showMessage($("#message"),`Registration confirmed! Registration ID: ${r.registration_id}. Ticket: ${r.ticket_id}. Keep your ticket code safe.`);
    e.target.reset(); $("#registration-form").elements.user_id.value=d.user_id;
    await loadEvents();
  } catch(err) { showMessage($("#message"),err.message,false); }
});
$("#ticket-form").addEventListener("submit", async e => {
  e.preventDefault(); const code=new FormData(e.target).get("ticket_id").trim();
  try {
    const t=await api(`${API.tickets}/tickets/${encodeURIComponent(code)}`);
    $("#ticket-result").innerHTML=`<div class="result success"><strong>${escapeHtml(t.ticket_id)}</strong><br>Event: ${escapeHtml(t.event_name)}<br>Date: ${escapeHtml(new Date(t.event_date).toLocaleString())}<br>Venue: ${escapeHtml(t.venue)}<br>Status: ${escapeHtml(t.status.toUpperCase())}</div>`;
  } catch(err) { showMessage($("#ticket-result"),err.message,false); }
});
$("#notification-form").addEventListener("submit", async e => {
  e.preventDefault(); const id=Number(new FormData(e.target).get("user_id"));
  try {
    const rows=await api(`${API.notifications}/notifications?user_id=${id}`);
    $("#notification-list").innerHTML=rows.length?rows.map(n=>`<div class="result"><strong>${escapeHtml(n.notification_type)}</strong> · ${escapeHtml(new Date(n.created_at).toLocaleString())}<br>${escapeHtml(n.message)}<br><small>${n.is_read?'Read':'Unread'}</small></div>`).join(""):'<p class="muted">No notifications for this user yet.</p>';
  } catch(err) { showMessage($("#notification-list"),err.message,false); }
});
loadEvents();
