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

  var repoCards = Array.prototype.slice.call(
    document.querySelectorAll("[data-repo]")
  );

  function measureRepoCard(item) {
    if (item.classList.contains("is-open")) {
      return;
    }
    var description = item.querySelector(".item-desc");
    if (!description) {
      return;
    }
    item.classList.toggle(
      "has-more",
      description.scrollHeight > description.clientHeight + 1
    );
  }

  function setRepoToggle(item, open) {
    var button = item.querySelector(".repo-toggle");
    if (!button) {
      return;
    }
    button.textContent = open ? "Less…" : "More…";
    button.setAttribute("aria-expanded", open ? "true" : "false");
  }

  function repoTransitionMs(description) {
    var value = getComputedStyle(description).transitionDuration || "0s";
    var parts = value.split(",").map(parseFloat);
    parts = parts.filter(function (part) {
      return !isNaN(part);
    });
    return parts.length ? Math.max.apply(null, parts) * 1000 : 0;
  }

  function repoPreviewHeight(description) {
    var value = getComputedStyle(description)
      .getPropertyValue("--repo-preview")
      .trim();
    var amount = parseFloat(value);
    if (isNaN(amount)) {
      return 0;
    }
    if (value.slice(-3) === "rem") {
      return (
        amount * parseFloat(getComputedStyle(document.documentElement).fontSize)
      );
    }
    return amount;
  }

  function animateRepo(item, open) {
    var description = item.querySelector(".item-desc");
    if (!description) {
      return;
    }

    var start = description.getBoundingClientRect().height;
    var end = open ? description.scrollHeight : repoPreviewHeight(description);

    description.style.overflow = "hidden";
    description.style.maxHeight = start + "px";
    void description.offsetHeight;

    item.classList.toggle("is-open", open);
    description.style.maxHeight = end + "px";

    if (item.repoTimer) {
      window.clearTimeout(item.repoTimer);
    }
    item.repoTimer = window.setTimeout(function () {
      description.style.maxHeight = "";
      description.style.overflow = "";
      item.repoTimer = null;
    }, repoTransitionMs(description) + 20);
  }

  if (repoCards.length) {
    repoCards.forEach(function (item) {
      var button = item.querySelector(".repo-toggle");
      if (!button) {
        measureRepoCard(item);
        return;
      }

      button.addEventListener("click", function () {
        var isOpen = item.classList.contains("is-open");

        repoCards.forEach(function (other) {
          if (other !== item && other.classList.contains("is-open")) {
            setRepoToggle(other, false);
            animateRepo(other, false);
          }
        });

        animateRepo(item, !isOpen);
        setRepoToggle(item, !isOpen);
      });

      measureRepoCard(item);
    });

    if (document.fonts && document.fonts.ready) {
      document.fonts.ready.then(function () {
        repoCards.forEach(measureRepoCard);
      });
    }

    window.addEventListener("resize", function () {
      repoCards.forEach(measureRepoCard);
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
