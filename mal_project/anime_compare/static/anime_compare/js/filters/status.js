import { getWrapperForm, resetPage, nextState } from "../utils/dom.js";
import { trigger } from "../utils/htmx.js";

function rebuildStatuses(wrapper, form) {
  form.querySelectorAll("input[name^='status_']").forEach(i => i.remove());

  wrapper
    .querySelectorAll(".status-filter .status-pill")
    .forEach(pill => {
      if (pill.dataset.state === "include" || pill.dataset.state === "exclude") {
        const input = document.createElement("input");
        input.type = "hidden";
        input.name =
          pill.dataset.state === "include"
            ? "status_include[]"
            : "status_exclude[]";
        input.value = pill.dataset.status;
        form.appendChild(input);
      }
    });

  resetPage(form);
}

document.addEventListener("click", e => {
  const pill = e.target.closest(".status-filter .status-pill");
  if (!pill) return;

  const { wrapper, form } = getWrapperForm(pill);
  if (!form) return;

  const next = nextState(pill.dataset.state);
  pill.dataset.state = next;
  pill.className = "status-pill " + next;

  rebuildStatuses(wrapper, form);
  trigger(form);
});
