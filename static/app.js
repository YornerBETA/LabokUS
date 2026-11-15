const $ = (id) => document.getElementById(id);
let token = localStorage.getItem("kolobok_access_token") || "";
let currentConversation = null;
let currentView = "chat";

async function api(path, options = {}) {
  const headers = {"Content-Type":"application/json", ...(options.headers || {})};
  if (token) headers.Authorization = "Bearer " + token;
  const response = await fetch(path, {...options, headers});
  const data = await response.json().catch(() => ({}));
  if (response.status === 401) {
    $("login").classList.remove("hidden");
    throw new Error(data.detail || "Требуется вход");
  }
  if (!response.ok) throw new Error(data.detail || "Ошибка запроса");
  return data;
}
function showError(error) { alert(error.message || String(error)); }
function switchView(view) {
  currentView = view;
  for (const name of ["chat","graph","system"]) $(name+"-view").classList.toggle("hidden", name !== view);
  document.querySelectorAll(".nav-item").forEach(el => el.classList.toggle("active", el.dataset.view === view));
  $("view-title").textContent = ({chat:"Чат",graph:"Граф знаний",system:"Состояние системы"})[view];
  if (view === "graph") loadNodes();
  if (view === "system") loadStatus();
}
function appendMessage(role, content) {
  const welcome = document.querySelector(".welcome");
  if (welcome) welcome.remove();
  const el = document.createElement("div");
  el.className = "message " + role;
  el.textContent = content;
  $("messages").appendChild(el);
  $("messages").scrollTop = $("messages").scrollHeight;
}
async function createConversation() {
  const data = await api("/api/conversations", {method:"POST", body:JSON.stringify({title:"Новый диалог"})});
  currentConversation = data.id;
  $("messages").innerHTML = "";
}
async function sendMessage(event) {
  event.preventDefault();
  const input = $("chat-input"), message = input.value.trim();
  if (!message) return;
  try {
    if (!currentConversation) await createConversation();
    appendMessage("user", message);
    input.value = "";
    $("send-button").disabled = true;
    const result = await api("/api/chat", {method:"POST", body:JSON.stringify({conversation_id:currentConversation,message})});
    appendMessage("assistant", result.message.content);
  } catch (error) {
    appendMessage("assistant", "Не удалось получить ответ: " + (error.message || error));
  } finally { $("send-button").disabled = false; }
}
async function loadNodes() {
  try {
    const q = $("node-search").value.trim();
    const nodes = await api("/api/nodes" + (q ? "?q="+encodeURIComponent(q) : ""));
    $("node-count").textContent = nodes.length + " узлов";
    const root = $("nodes-list");
    root.innerHTML = "";
    for (const node of nodes) {
      const card = document.createElement("article");
      card.className = "node-card";
      const title = document.createElement("h3"); title.textContent = node.name;
      const content = document.createElement("p"); content.textContent = node.content || "Нет описания";
      const meta = document.createElement("div"); meta.className = "node-meta";
      [node.node_type,node.importance,...(node.tags || [])].forEach(value => {
        const tag = document.createElement("span"); tag.className = "tag"; tag.textContent = value; meta.appendChild(tag);
      });
      const id = document.createElement("small"); id.textContent = "ID: " + node.id; id.style.color = "#71819c";
      card.append(title,content,meta,id); root.appendChild(card);
    }
    if (!nodes.length) root.textContent = "Пока нет узлов. Добавь первую запись в память Колобка.";
  } catch (error) { showError(error); }
}
async function loadStatus() {
  try {
    const s = await api("/api/status");
    $("provider-label").textContent = s.model_configured ? s.provider + " · " + s.model : "Модель не настроена";
    const entries = [
      ["API-сервер","Работает","FastAPI"],
      ["AI-провайдер",s.model_configured ? "Настроен" : "Не настроен",s.provider],
      ["Граф знаний","Работает","SQLite"],
      ["Агент компьютера","Не подключён","Требуется отдельный локальный клиент"],
      ["Облачные задачи","Следующий этап","Очередь и фоновые workers ещё не созданы"],
      ["Хранилище","Локальная БД","На бесплатном Render данные могут быть временными"]
    ];
    $("system-cards").innerHTML = "";
    for (const [name,state,detail] of entries) {
      const card = document.createElement("div"); card.className = "system-card";
      const strong = document.createElement("strong"); strong.textContent = state;
      const span = document.createElement("span"); span.textContent = name + " · " + detail;
      card.append(strong,span); $("system-cards").appendChild(card);
    }
  } catch (error) { showError(error); }
}
$("chat-form").addEventListener("submit", sendMessage);
$("new-chat").addEventListener("click", () => createConversation().catch(showError));
$("node-search").addEventListener("input", () => loadNodes());
$("refresh-status").addEventListener("click", () => loadStatus());
document.querySelectorAll(".nav-item").forEach(el => el.addEventListener("click", () => switchView(el.dataset.view)));
$("add-node").addEventListener("click", () => $("node-dialog").showModal());
$("cancel-node").addEventListener("click", () => $("node-dialog").close());
$("node-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    await api("/api/nodes", {method:"POST",body:JSON.stringify({
      name:$("node-name").value.trim(), node_type:$("node-type").value.trim() || "note",
      content:$("node-content").value, tags:$("node-tags").value.split(",").map(x=>x.trim()).filter(Boolean),
      importance:$("node-importance").value, source:$("node-source").value.trim() || null
    })});
    $("node-dialog").close(); $("node-form").reset(); $("node-type").value="note"; loadNodes();
  } catch (error) { showError(error); }
});
$("login-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    const value = $("access-token").value;
    await fetch("/api/login",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({token:value})}).then(async r=>{if(!r.ok)throw new Error((await r.json()).detail || "Вход не выполнен");});
    token=value; localStorage.setItem("kolobok_access_token",token); $("login").classList.add("hidden"); initialize();
  } catch (error) { $("login-error").textContent = error.message; }
});
$("logout").addEventListener("click", () => {token="";localStorage.removeItem("kolobok_access_token");$("login").classList.remove("hidden");});
async function initialize() {
  try {
    await api("/api/status");
    $("login").classList.add("hidden");
    $("connection-dot").style.background="var(--green)";
    $("connection-label").textContent="Сервер подключён";
    await createConversation();
    await loadStatus();
  } catch (error) {
    if (error.message !== "Требуется вход") {
      $("connection-label").textContent="Ошибка подключения";
      $("connection-dot").style.background="var(--red)";
    }
  }
}
initialize();
