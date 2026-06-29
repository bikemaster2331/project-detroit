const $ = (id) => document.getElementById(id);

function agentId() {
  return $("agentId").value.trim();
}

function addMessage(role, text) {
  if (!text) return;
  const item = document.createElement("div");
  item.className = `message ${role}`;
  item.textContent = `${role === "user" ? "You" : "Detroit"}: ${text}`;
  $("chat").appendChild(item);
  $("chat").scrollTop = $("chat").scrollHeight;
}

async function jsonFetch(url, options = {}) {
  const response = await fetch(url, {
    headers: {"Content-Type": "application/json"},
    ...options,
  });
  if (!response.ok) {
    const body = await response.text();
    throw new Error(`${response.status}: ${body}`);
  }
  return response.json();
}

async function createAgent() {
  const data = await jsonFetch("/api/agents", {
    method: "POST",
    body: JSON.stringify({agent_id: agentId(), name: "Detroit"}),
  });
  $("state").textContent = JSON.stringify(data.state, null, 2);
}

async function refreshState() {
  const data = await jsonFetch(`/api/agents/${agentId()}`);
  $("state").textContent = JSON.stringify(data.state, null, 2);
}

async function sendMessage() {
  const message = $("message").value.trim();
  if (!message) return;

  addMessage("user", message);
  $("message").value = "";

  const data = await jsonFetch(`/api/agents/${agentId()}/interact`, {
    method: "POST",
    body: JSON.stringify({
      message,
      topic: $("topic").value.trim() || null,
      valence: Number($("valence").value),
      novelty: Number($("novelty").value),
      importance: Number($("importance").value),
      unresolved: $("unresolved").checked,
    }),
  });

  addMessage("agent", data.decision.content);
  $("decision").textContent = JSON.stringify(data.decision, null, 2);
  $("state").textContent = JSON.stringify(data.agent.state, null, 2);
}

async function simulateTime() {
  const data = await jsonFetch(`/api/agents/${agentId()}/tick`, {
    method: "POST",
    body: JSON.stringify({minutes: 60}),
  });
  $("decision").textContent = JSON.stringify(data.decision, null, 2);
  $("state").textContent = JSON.stringify(data.agent.state, null, 2);
  addMessage("agent", data.decision.content);
}

async function pollOutbox() {
  const id = agentId();
  if (!id) return;
  try {
    const messages = await jsonFetch(`/api/agents/${id}/outbox`);
    for (const message of messages) {
      addMessage("agent", message.content);
    }
  } catch (_) {
    // Agent may not exist yet.
  }
}

$("createAgent").addEventListener("click", () => createAgent().catch(alert));
$("send").addEventListener("click", () => sendMessage().catch(alert));
$("tick").addEventListener("click", () => simulateTime().catch(alert));
$("refresh").addEventListener("click", () => refreshState().catch(alert));

setInterval(pollOutbox, 5000);
