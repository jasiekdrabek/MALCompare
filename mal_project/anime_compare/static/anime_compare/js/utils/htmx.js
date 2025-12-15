export function trigger(form) {
  if (form) {
    htmx.trigger(form, "tablechange");
  }
}
