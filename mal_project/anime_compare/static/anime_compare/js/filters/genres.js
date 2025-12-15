import { getWrapperForm, nextState, rebuildGenres } from "../utils/dom.js";
import { trigger } from "../utils/htmx.js";

document.addEventListener("click", e => {
  const pill = e.target.closest(".genre-checkboxes .genre-pill");
  if (!pill) return;

  const wrapper = pill.closest(".genre-filter");
  const { form } = getWrapperForm(pill);
  if (!wrapper || !form) return;

  const next = nextState(pill.dataset.state);
  pill.dataset.state = next;
  pill.className = "genre-pill " + next;

  rebuildGenres(wrapper, form);
  trigger(form);
});

document.addEventListener("click", e => {
  const summaryPill = e.target.closest(".genre-summary-pill");
  if (!summaryPill) return;
  const {wrapper, form } = getWrapperForm(summaryPill);
  if (!wrapper || !form) return;
  const tableType = wrapper.dataset.tableType;
  const wrapperTable = document.querySelector(`.genre-container-${tableType}`);
  if (!wrapperTable) return;
  const genre = summaryPill.dataset.genre;

  const original = wrapper.querySelector(
    `.genre-checkboxes .genre-pill[data-genre="${genre}"]`
  );
  if (!original) return;
  const next = nextState(original.dataset.state);
  original.dataset.state = next;
  original.className = "genre-pill " + next;

  rebuildGenres(wrapper, form);
  trigger(form);
});
