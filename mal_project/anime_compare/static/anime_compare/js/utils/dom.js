export function getWrapperForm(el) {
  const wrapper = el.closest(".table-wrapper");
  if (!wrapper) return {};
  return {
    wrapper,
    form: wrapper.querySelector(".table-state")
  };
}

export function resetPage(form) {
  const pageInput = form?.querySelector("input[name^='page_']");
  if (pageInput) pageInput.value = 1;
}

export function setValue(form, name, value) {
  const input = form.querySelector(`input[name='${name}']`);
  if (input) input.value = value;
}

export function nextState(current) {
  const states = ["neutral", "include", "exclude"];
  return states[(states.indexOf(current) + 1) % 3];
}

export function rebuildGenres(wrapper, form) {
  form.querySelectorAll("input[name^='genres_']").forEach(i => i.remove());

  wrapper
    .querySelectorAll(".genre-checkboxes .genre-pill")
    .forEach(pill => {
      if (pill.dataset.state === "include" || pill.dataset.state === "exclude") {
        const input = document.createElement("input");
        input.type = "hidden";
        input.name =
          pill.dataset.state === "include"
            ? "genres_include[]"
            : "genres_exclude[]";
        input.value = pill.dataset.genre;
        form.appendChild(input);
      }
    });

  resetPage(form);
}

export function rebuildRange(form, minName, maxName, min, max) {
  form
    .querySelectorAll(`input[name='${minName}'], input[name='${maxName}']`)
    .forEach(i => i.remove());

  if (min !== "") {
    const i = document.createElement("input");
    i.type = "hidden";
    i.name = minName;
    i.value = min;
    form.appendChild(i);
  }

  if (max !== "") {
    const i = document.createElement("input");
    i.type = "hidden";
    i.name = maxName;
    i.value = max;
    form.appendChild(i);
  }

  resetPage(form);
}