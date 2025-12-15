import { getWrapperForm, setValue, resetPage } from "../utils/dom.js";
import { trigger } from "../utils/htmx.js";

document.addEventListener("click", e => {
  const btn = e.target.closest(".reset-filters");
  if (!btn) return;

  const { form } = getWrapperForm(btn);
  if (!form) return;

  setValue(form, "score_min", 1);
  setValue(form, "score_max", 10);
  setValue(form, "ep_min", 1);
  setValue(form, "ep_max", 2000);
  setValue(form, "sort", "title");
  setValue(form, "dir", "asc");

  resetPage(form);

  form.querySelectorAll(
    "input[name='genres_include[]'], input[name='genres_exclude[]'], " +
    "input[name='status_include[]'], input[name='status_exclude[]']"
  ).forEach(i => i.remove());

  trigger(form);
});
