import { getWrapperForm, rebuildRange } from "../utils/dom.js";
import { trigger } from "../utils/htmx.js";

document.addEventListener("click", e => {
  const btn = e.target.closest(".apply-score");
  if (!btn) return;

  const { wrapper, form } = getWrapperForm(btn);
  rebuildRange(
    form,
    "score_min",
    "score_max",
    wrapper.querySelector("[data-filter='score_min']").value,
    wrapper.querySelector("[data-filter='score_max']").value
  );

  trigger(form);
});
