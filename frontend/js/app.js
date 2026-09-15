const API_BASE = "";

const dateInput = document.getElementById("date-input");
const checkBtn = document.getElementById("check-availability-btn");
const loadingEl = document.getElementById("loading");

const feedbackSection = document.getElementById("feedback-section");
const feedbackMessage = document.getElementById("feedback-message");

const slotsSection = document.getElementById("slots-section");
const slotsGrid = document.getElementById("slots-grid");
const bookedListWrapper = document.getElementById("booked-list-wrapper");
const bookedList = document.getElementById("booked-list");

const formSection = document.getElementById("form-section");
const formDate = document.getElementById("form-date");
const formTime = document.getElementById("form-time");
const patientNameInput = document.getElementById("patient-name");
const patientPhoneInput = document.getElementById("patient-phone");
const formError = document.getElementById("form-error");
const cancelBtn = document.getElementById("cancel-btn");
const confirmBtn = document.getElementById("confirm-btn");

const resultSection = document.getElementById("result-section");
const resultMessage = document.getElementById("result-message");
const newAppointmentBtn = document.getElementById("new-appointment-btn");

const state = {
  date: null,
  time: null,
  selectedSlotBtn: null,
};

function setLoading(isLoading) {
  loadingEl.hidden = !isLoading;
}

function hideSections(...sections) {
  sections.forEach((section) => {
    section.hidden = true;
  });
}

async function fetchJson(url, options) {
  const response = await fetch(url, options);
  const data = await response.json().catch(() => ({}));
  return { ok: response.ok, status: response.status, data };
}

function showFeedback(message) {
  feedbackMessage.textContent = message;
  feedbackMessage.className = "feedback-warning";
  feedbackSection.hidden = false;
}

function renderSlots(slots) {
  slotsGrid.innerHTML = "";
  state.selectedSlotBtn = null;

  slots.forEach((time) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "slot-btn";
    btn.textContent = time;
    btn.addEventListener("click", () => selectSlot(time, btn));
    slotsGrid.appendChild(btn);
  });
}

async function loadBookedAppointments(dateStr) {
  try {
    const { ok, data } = await fetchJson(`${API_BASE}/appointments?date=${dateStr}`);

    if (!ok || data.length === 0) {
      bookedListWrapper.hidden = true;
      return;
    }

    bookedList.innerHTML = "";
    data.forEach((item) => {
      const li = document.createElement("li");
      li.textContent = `${item.appointment_time} — ${item.patient_name}`;
      bookedList.appendChild(li);
    });
    bookedListWrapper.hidden = false;
  } catch (err) {
    bookedListWrapper.hidden = true;
  }
}

async function loadAvailability(dateStr) {
  hideSections(feedbackSection, slotsSection, formSection, resultSection);
  setLoading(true);

  try {
    const { ok, data } = await fetchJson(`${API_BASE}/available?date=${dateStr}`);

    if (!ok) {
      showFeedback(data.error || "Não foi possível verificar a disponibilidade.");
      return;
    }

    if (!data.available) {
      showFeedback(data.reason || "Data indisponível para agendamento.");
      return;
    }

    if (data.slots.length === 0) {
      showFeedback("Não há horários livres nesta data.");
      return;
    }

    renderSlots(data.slots);
    slotsSection.hidden = false;
    await loadBookedAppointments(dateStr);
  } catch (err) {
    showFeedback("Erro de conexão com o servidor. Tente novamente.");
  } finally {
    setLoading(false);
  }
}

async function refreshAvailabilityView(dateStr) {
  const { ok, data } = await fetchJson(`${API_BASE}/available?date=${dateStr}`);
  if (ok && data.available && data.slots.length > 0) {
    renderSlots(data.slots);
    slotsSection.hidden = false;
  } else {
    slotsSection.hidden = true;
  }
  await loadBookedAppointments(dateStr);
}

function checkAvailability() {
  const dateStr = dateInput.value;
  if (!dateStr) {
    hideSections(slotsSection, formSection, resultSection);
    showFeedback("Selecione uma data.");
    return;
  }
  state.date = dateStr;
  loadAvailability(dateStr);
}

function selectSlot(time, btnEl) {
  if (state.selectedSlotBtn) {
    state.selectedSlotBtn.classList.remove("selected");
  }
  btnEl.classList.add("selected");
  state.selectedSlotBtn = btnEl;
  state.time = time;

  formDate.textContent = state.date;
  formTime.textContent = time;
  patientNameInput.value = "";
  patientPhoneInput.value = "";
  formError.hidden = true;
  formSection.hidden = false;
  updateConfirmState();
  patientNameInput.focus();
}

function updateConfirmState() {
  confirmBtn.disabled = patientNameInput.value.trim().length === 0;
}

function resetSelection() {
  if (state.selectedSlotBtn) {
    state.selectedSlotBtn.classList.remove("selected");
    state.selectedSlotBtn = null;
  }
  state.time = null;
  formSection.hidden = true;
}

async function confirmAppointment() {
  formError.hidden = true;
  setLoading(true);
  confirmBtn.disabled = true;

  try {
    const { status, data } = await fetchJson(`${API_BASE}/appointments`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        patient_name: patientNameInput.value.trim(),
        patient_phone: patientPhoneInput.value.trim() || null,
        appointment_date: state.date,
        appointment_time: state.time,
      }),
    });

    if (status === 201) {
      resetSelection();
      slotsSection.hidden = true;
      resultMessage.textContent =
        `Agendamento confirmado para ${data.appointment_date} às ${data.appointment_time}, ` +
        `paciente ${data.patient_name}.`;
      resultMessage.className = "feedback-success";
      newAppointmentBtn.hidden = false;
      resultSection.hidden = false;
      return;
    }

    if (status === 409) {
      resetSelection();
      showFeedback(data.error || "Esse horário não está mais disponível. Escolha outro.");
      await refreshAvailabilityView(state.date);
      return;
    }

    if (status === 400) {
      formError.textContent = data.error || "Dados inválidos.";
      formError.hidden = false;
      return;
    }

    formError.textContent = "Erro inesperado ao confirmar o agendamento.";
    formError.hidden = false;
  } catch (err) {
    formError.textContent = "Erro de conexão com o servidor. Tente novamente.";
    formError.hidden = false;
  } finally {
    setLoading(false);
    updateConfirmState();
  }
}

function onNewAppointment() {
  resultSection.hidden = true;
  loadAvailability(state.date);
}

checkBtn.addEventListener("click", checkAvailability);
dateInput.addEventListener("change", checkAvailability);
cancelBtn.addEventListener("click", resetSelection);
confirmBtn.addEventListener("click", confirmAppointment);
newAppointmentBtn.addEventListener("click", onNewAppointment);
patientNameInput.addEventListener("input", updateConfirmState);
