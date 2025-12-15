document.addEventListener("click", e => {
  const btn = e.target.closest(".toggle-filters");
  if (!btn) return;

  const wrapper = btn.closest(".table-wrapper");
  const filters = wrapper.querySelector(".filters");
  const summary = wrapper.querySelector(".filters-summary");
  const input = wrapper.querySelector("input[name='filters_open']");

  const isOpen = filters.classList.toggle("is-open");
  input.value = isOpen ? "1" : "0";

  btn.textContent = isOpen ? "Ukryj filtry" : "Pokaż filtry";
  summary.classList.toggle("d-none", isOpen);
});
