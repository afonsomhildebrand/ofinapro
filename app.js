const storeKey = "oficina-pro-data";

const initialData = {
  clients: [
    { id: "c1", name: "Mariana Costa", phone: "(11) 98888-1111", email: "mariana@email.com", document: "123.456.789-00" },
    { id: "c2", name: "Rafael Lima", phone: "(21) 97777-2222", email: "rafael@email.com", document: "987.654.321-00" }
  ],
  cars: [
    { id: "car1", clientId: "c1", manufacturer: "Toyota", model: "Corolla", year: 2019, plate: "ABC1D23", mileage: 82000 },
    { id: "car2", clientId: "c2", manufacturer: "Chevrolet", model: "Onix", year: 2021, plate: "XYZ9A87", mileage: 41000 }
  ],
  employees: [
    { id: "e1", name: "Joao Silva", role: "Mecanico", phone: "(11) 95555-3333", hourlyCost: 48 },
    { id: "e2", name: "Ana Rocha", role: "Eletricista", phone: "(11) 94444-4444", hourlyCost: 55 }
  ],
  parts: [
    { id: "p1", name: "Filtro de oleo", sku: "FLT-001", stock: 12, cost: 28, price: 48 },
    { id: "p2", name: "Pastilha de freio", sku: "FR-220", stock: 8, cost: 120, price: 190 },
    { id: "p3", name: "Vela de ignicao", sku: "IGN-014", stock: 16, cost: 32, price: 58 }
  ],
  services: [
    { id: "s1", name: "Troca de oleo", description: "Substituicao de oleo e filtro", basePrice: 180, estimatedHours: 1 },
    { id: "s2", name: "Revisao de freios", description: "Inspecao e troca de componentes", basePrice: 420, estimatedHours: 2.5 },
    { id: "s3", name: "Diagnostico eletrico", description: "Analise de falhas eletricas", basePrice: 260, estimatedHours: 1.5 }
  ],
  orders: [
    { id: "o1", clientId: "c1", carId: "car1", serviceId: "s1", employeeId: "e1", status: "Concluida", hoursSpent: 1.25, chargedValue: 220, partIds: ["p1"] },
    { id: "o2", clientId: "c2", carId: "car2", serviceId: "s2", employeeId: "e2", status: "Em andamento", hoursSpent: 2.75, chargedValue: 560, partIds: ["p2"] }
  ]
};

let data = loadData();

const titles = {
  dashboard: ["Painel", "Resumo financeiro, tempos medios e fluxo da oficina."],
  clientes: ["Clientes", "Cadastro e contato dos clientes da oficina."],
  carros: ["Carros", "Veiculos por cliente, fabricante, modelo e ano."],
  funcionarios: ["Funcionarios", "Equipe, cargos e custo por hora."],
  pecas: ["Pecas", "Estoque, custo e preco de venda."],
  servicos: ["Servicos", "Tabela de servicos, preco padrao e tempo estimado."],
  ordens: ["Ordens de servico", "Servico por carro, funcionario, custo, valor e tempo gasto."]
};

function loadData() {
  const saved = localStorage.getItem(storeKey);
  return saved ? JSON.parse(saved) : structuredClone(initialData);
}

function saveData() {
  localStorage.setItem(storeKey, JSON.stringify(data));
}

function money(value) {
  return Number(value || 0).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

function hours(value) {
  const number = Number(value || 0);
  return `${number.toLocaleString("pt-BR", { maximumFractionDigits: 2 })}h`;
}

function makeId(prefix) {
  return `${prefix}-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function byId(collection, id) {
  return collection.find((item) => item.id === id);
}

function partCost(order) {
  return order.partIds.reduce((sum, id) => sum + Number(byId(data.parts, id)?.cost || 0), 0);
}

function laborCost(order) {
  const employee = byId(data.employees, order.employeeId);
  return Number(order.hoursSpent || 0) * Number(employee?.hourlyCost || 0);
}

function orderCost(order) {
  return partCost(order) + laborCost(order);
}

function selectedValues(select) {
  return Array.from(select.selectedOptions).map((option) => option.value);
}

function fillSelect(select, items, label, placeholder = "Selecione") {
  select.innerHTML = `<option value="">${placeholder}</option>`;
  items.forEach((item) => {
    const option = document.createElement("option");
    option.value = item.id;
    option.textContent = label(item);
    select.appendChild(option);
  });
}

function fillMultiSelect(select, items, label) {
  select.innerHTML = "";
  items.forEach((item) => {
    const option = document.createElement("option");
    option.value = item.id;
    option.textContent = label(item);
    select.appendChild(option);
  });
}

function syncSelects() {
  document.querySelectorAll('select[name="clientId"]').forEach((select) => fillSelect(select, data.clients, (client) => client.name));
  document.querySelectorAll('select[name="carId"]').forEach((select) => fillSelect(select, data.cars, (car) => {
    const client = byId(data.clients, car.clientId)?.name || "Sem cliente";
    return `${car.manufacturer} ${car.model} ${car.year} - ${car.plate} (${client})`;
  }));
  document.querySelectorAll('select[name="serviceId"]').forEach((select) => fillSelect(select, data.services, (service) => `${service.name} - ${money(service.basePrice)}`));
  document.querySelectorAll('select[name="employeeId"]').forEach((select) => fillSelect(select, data.employees, (employee) => `${employee.name} - ${employee.role}`));
  document.querySelectorAll('select[name="partIds"]').forEach((select) => fillMultiSelect(select, data.parts, (part) => `${part.name} - ${money(part.price)}`));
}

function renderCards(targetId, items, render, editType) {
  const target = document.getElementById(targetId);
  if (!items.length) {
    target.innerHTML = '<div class="empty">Nenhum cadastro encontrado.</div>';
    return;
  }
  target.innerHTML = items.map((item) => `
    <article class="card">
      ${render(item)}
      <div class="card-actions">
        <button class="secondary-button" type="button" data-edit="${editType}" data-id="${item.id}">Editar</button>
        <button class="danger-button" type="button" data-delete="${editType}" data-id="${item.id}">Excluir</button>
      </div>
    </article>
  `).join("");
}

function renderDashboard() {
  const revenue = data.orders.reduce((sum, order) => sum + Number(order.chargedValue || 0), 0);
  const partsCost = data.orders.reduce((sum, order) => sum + partCost(order), 0);
  const totalCost = data.orders.reduce((sum, order) => sum + orderCost(order), 0);
  const avgTime = data.orders.length ? data.orders.reduce((sum, order) => sum + Number(order.hoursSpent || 0), 0) / data.orders.length : 0;

  document.getElementById("metricRevenue").textContent = money(revenue);
  document.getElementById("metricPartsCost").textContent = money(partsCost);
  document.getElementById("metricProfit").textContent = money(revenue - totalCost);
  document.getElementById("metricAverageTime").textContent = hours(avgTime);

  const grouped = data.services.map((service) => {
    const orders = data.orders.filter((order) => order.serviceId === service.id);
    const count = orders.length;
    const charged = count ? orders.reduce((sum, order) => sum + Number(order.chargedValue || 0), 0) / count : 0;
    const time = count ? orders.reduce((sum, order) => sum + Number(order.hoursSpent || 0), 0) / count : 0;
    const profit = count ? orders.reduce((sum, order) => sum + (Number(order.chargedValue || 0) - orderCost(order)), 0) / count : 0;
    return { service, count, charged, time, profit };
  });

  document.getElementById("serviceAverages").innerHTML = grouped.map((row) => `
    <tr>
      <td>${row.service.name}</td>
      <td>${row.count}</td>
      <td>${money(row.charged)}</td>
      <td>${hours(row.time)}</td>
      <td>${money(row.profit)}</td>
    </tr>
  `).join("");

  const maxOrders = Math.max(1, ...data.employees.map((employee) => data.orders.filter((order) => order.employeeId === employee.id).length));
  document.getElementById("employeeStats").innerHTML = data.employees.map((employee) => {
    const orders = data.orders.filter((order) => order.employeeId === employee.id);
    const percent = Math.round((orders.length / maxOrders) * 100);
    const revenueByEmployee = orders.reduce((sum, order) => sum + Number(order.chargedValue || 0), 0);
    return `
      <div class="stat-row">
        <strong><span>${employee.name}</span><span>${orders.length} serv.</span></strong>
        <div class="bar"><span style="width: ${percent}%"></span></div>
        <small>${money(revenueByEmployee)} faturados</small>
      </div>
    `;
  }).join("");
}

function renderOrders() {
  const tbody = document.getElementById("ordersTable");
  if (!data.orders.length) {
    tbody.innerHTML = '<tr><td colspan="9" class="empty">Nenhuma ordem cadastrada.</td></tr>';
    return;
  }
  tbody.innerHTML = data.orders.map((order) => {
    const client = byId(data.clients, order.clientId);
    const car = byId(data.cars, order.carId);
    const service = byId(data.services, order.serviceId);
    const employee = byId(data.employees, order.employeeId);
    return `
      <tr>
        <td>${client?.name || "-"}</td>
        <td>${car ? `${car.manufacturer} ${car.model} ${car.year}<br><small>${car.plate}</small>` : "-"}</td>
        <td>${service?.name || "-"}</td>
        <td>${employee?.name || "-"}</td>
        <td>${order.status}</td>
        <td>${hours(order.hoursSpent)}</td>
        <td>${money(orderCost(order))}</td>
        <td>${money(order.chargedValue)}</td>
        <td>
          <button class="secondary-button" type="button" data-edit="orders" data-id="${order.id}">Editar</button>
          <button class="danger-button" type="button" data-delete="orders" data-id="${order.id}">Excluir</button>
        </td>
      </tr>
    `;
  }).join("");
}

function renderAll() {
  syncSelects();
  renderDashboard();
  renderCards("clientsList", data.clients, (client) => `
    <h3>${client.name}</h3>
    <p>${client.phone}</p>
    <p>${client.email || "Sem email"}</p>
    <small>${client.document || "Sem documento"}</small>
  `, "clients");
  renderCards("carsList", data.cars, (car) => `
    <h3>${car.manufacturer} ${car.model}</h3>
    <p>${car.year} - ${car.plate}</p>
    <p>${byId(data.clients, car.clientId)?.name || "Cliente nao encontrado"}</p>
    <small>${Number(car.mileage || 0).toLocaleString("pt-BR")} km</small>
  `, "cars");
  renderCards("employeesList", data.employees, (employee) => `
    <h3>${employee.name}</h3>
    <p>${employee.role}</p>
    <p>${employee.phone || "Sem telefone"}</p>
    <small>Custo hora: ${money(employee.hourlyCost)}</small>
  `, "employees");
  renderCards("partsList", data.parts, (part) => `
    <h3>${part.name}</h3>
    <p>Codigo: ${part.sku}</p>
    <p>Estoque: ${part.stock}</p>
    <small>Custo ${money(part.cost)} | Venda ${money(part.price)}</small>
  `, "parts");
  renderCards("servicesList", data.services, (service) => `
    <h3>${service.name}</h3>
    <p>${service.description || "Sem descricao"}</p>
    <p>Preco padrao: ${money(service.basePrice)}</p>
    <small>Tempo estimado: ${hours(service.estimatedHours)}</small>
  `, "services");
  renderOrders();
}

function bindForm(formId, collectionName, prefix, mapper) {
  const form = document.getElementById(formId);
  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const formData = new FormData(form);
    const item = mapper(formData, form);
    const id = formData.get("id");
    if (id) {
      data[collectionName] = data[collectionName].map((current) => current.id === id ? { ...current, ...item, id } : current);
    } else {
      data[collectionName].push({ ...item, id: makeId(prefix) });
    }
    form.reset();
    saveData();
    renderAll();
  });
}

function fillForm(type, item) {
  const forms = {
    clients: "clientForm",
    cars: "carForm",
    employees: "employeeForm",
    parts: "partForm",
    services: "serviceForm",
    orders: "orderForm"
  };
  const form = document.getElementById(forms[type]);
  Object.entries(item).forEach(([key, value]) => {
    const field = form.elements[key];
    if (!field) return;
    if (field.multiple) {
      Array.from(field.options).forEach((option) => {
        option.selected = value.includes(option.value);
      });
    } else {
      field.value = value;
    }
  });
  form.scrollIntoView({ behavior: "smooth", block: "start" });
}

function removeItem(type, id) {
  data[type] = data[type].filter((item) => item.id !== id);
  saveData();
  renderAll();
}

document.querySelector(".nav").addEventListener("click", (event) => {
  const button = event.target.closest("[data-view]");
  if (!button) return;
  document.querySelectorAll(".nav-item").forEach((item) => item.classList.remove("active"));
  document.querySelectorAll(".view").forEach((view) => view.classList.remove("active"));
  button.classList.add("active");
  document.getElementById(button.dataset.view).classList.add("active");
  document.getElementById("viewTitle").textContent = titles[button.dataset.view][0];
  document.getElementById("viewSubtitle").textContent = titles[button.dataset.view][1];
});

document.body.addEventListener("click", (event) => {
  const edit = event.target.closest("[data-edit]");
  const del = event.target.closest("[data-delete]");
  if (edit) {
    fillForm(edit.dataset.edit, byId(data[edit.dataset.edit], edit.dataset.id));
  }
  if (del && confirm("Deseja excluir este registro?")) {
    removeItem(del.dataset.delete, del.dataset.id);
  }
});

document.getElementById("seedButton").addEventListener("click", () => {
  if (!confirm("Repor os dados de exemplo vai substituir os cadastros atuais. Continuar?")) return;
  data = structuredClone(initialData);
  saveData();
  renderAll();
});

bindForm("clientForm", "clients", "cli", (formData) => ({
  name: formData.get("name").trim(),
  phone: formData.get("phone").trim(),
  email: formData.get("email").trim(),
  document: formData.get("document").trim()
}));

bindForm("carForm", "cars", "car", (formData) => ({
  clientId: formData.get("clientId"),
  manufacturer: formData.get("manufacturer").trim(),
  model: formData.get("model").trim(),
  year: Number(formData.get("year")),
  plate: formData.get("plate").trim().toUpperCase(),
  mileage: Number(formData.get("mileage") || 0)
}));

bindForm("employeeForm", "employees", "fun", (formData) => ({
  name: formData.get("name").trim(),
  role: formData.get("role").trim(),
  phone: formData.get("phone").trim(),
  hourlyCost: Number(formData.get("hourlyCost"))
}));

bindForm("partForm", "parts", "pec", (formData) => ({
  name: formData.get("name").trim(),
  sku: formData.get("sku").trim().toUpperCase(),
  stock: Number(formData.get("stock")),
  cost: Number(formData.get("cost")),
  price: Number(formData.get("price"))
}));

bindForm("serviceForm", "services", "srv", (formData) => ({
  name: formData.get("name").trim(),
  description: formData.get("description").trim(),
  basePrice: Number(formData.get("basePrice")),
  estimatedHours: Number(formData.get("estimatedHours"))
}));

bindForm("orderForm", "orders", "ord", (formData, form) => ({
  clientId: formData.get("clientId"),
  carId: formData.get("carId"),
  serviceId: formData.get("serviceId"),
  employeeId: formData.get("employeeId"),
  status: formData.get("status"),
  hoursSpent: Number(formData.get("hoursSpent")),
  chargedValue: Number(formData.get("chargedValue")),
  partIds: selectedValues(form.elements.partIds)
}));

renderAll();
