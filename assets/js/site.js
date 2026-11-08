(function () {
  "use strict";

  var form = document.querySelector(".contact-form");
  if (form) {
    form.addEventListener("submit", function (event) {
      event.preventDefault();

      var email = form.getAttribute("data-email");
      var name = form.elements.namedItem("name").value.trim();
      var from = form.elements.namedItem("email").value.trim();
      var message = form.elements.namedItem("message").value.trim();

      if (!message) {
        return;
      }

      var subject = "Portfolio message" + (name ? " from " + name : "");
      var bodyLines = [message, ""];
      if (name) {
        bodyLines.push("From: " + name);
      }
      if (from) {
        bodyLines.push("Email: " + from);
      }

      var href =
        "mailto:" +
        encodeURIComponent(email).replace(/%40/g, "@") +
        "?subject=" +
        encodeURIComponent(subject) +
        "&body=" +
        encodeURIComponent(bodyLines.join("\n"));

      window.location.href = href;
    });
  }

  var copyButtons = document.querySelectorAll("[data-copy]");
  copyButtons.forEach(function (button) {
    button.addEventListener("click", function () {
      var value = button.getAttribute("data-copy");
      var original = button.textContent;

      function done() {
        button.textContent = "Copied";
        window.setTimeout(function () {
          button.textContent = original;
        }, 1500);
      }

      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(value).then(done, function () {
          window.prompt("Copy this address:", value);
        });
      } else {
        window.prompt("Copy this address:", value);
      }
    });
  });
})();
