"use strict";
const form = document.querySelector("#plan-form");
if (form) {
  form.addEventListener("submit", () => {
    const button = form.querySelector("button[type='submit']");
    if (button && form.reportValidity()) {
      button.disabled = true;
      button.querySelector("span").textContent = "Building your plan…";
    }
  });
}
