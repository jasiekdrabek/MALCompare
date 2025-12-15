import { getWrapperForm, rebuildRange } from "../utils/dom.js";
import { trigger } from "../utils/htmx.js";

document.addEventListener("click", e => {
  const btn = e.target.closest(".apply-episodes");
  if (!btn) return;

  const { wrapper, form } = getWrapperForm(btn);
  rebuildRange(
      form,
      "ep_min",
      "ep_max",
      wrapper.querySelector("[data-filter='ep_min']").value,
      wrapper.querySelector("[data-filter='ep_max']").value
    );
  trigger(form);
});
