import { getWrapperForm } from "../utils/dom.js";
import { trigger } from "../utils/htmx.js";

document.addEventListener("click", e => {
  const btn =
    e.target.closest(".page-prev") ||
    e.target.closest(".page-next");

  if (!btn || btn.disabled) return;

  const { form } = getWrapperForm(btn);
  if (!form) return;
  const pageInput = form.querySelector("input[name^='page_']");
  if (!pageInput) return;

  pageInput.value =
    parseInt(pageInput.value, 10) + (btn.classList.contains("page-next") ? 1 : -1);

  trigger(form);
});
