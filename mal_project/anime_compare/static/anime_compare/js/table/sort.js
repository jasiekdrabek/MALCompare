import { getWrapperForm, resetPage } from "../utils/dom.js";
import { trigger } from "../utils/htmx.js";

document.addEventListener("click", e => {
  const header = e.target.closest(".sort-header");
  if (!header) return;

  const { form } = getWrapperForm(header);
  if (!form) return;

  const sortInput = form.querySelector("input[name='sort']");
  const dirInput = form.querySelector("input[name='dir']");

  let nextDir = "asc";
  if (header.dataset.active === "1") {
    nextDir =
      header.dataset.dir === "asc"
        ? "desc"
        : header.dataset.dir === "desc"
        ? ""
        : "asc";
  }

  sortInput.value = nextDir ? header.dataset.sort : "";
  dirInput.value = nextDir;

  resetPage(form);
  trigger(form);
});
