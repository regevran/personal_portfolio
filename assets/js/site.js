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

  // Species decks: hovering or keyboard focus fans the deck open. Pressing a
  // fanned card presents it; pressing the presented card returns it to the
  // fan. Leaving hover closes the deck with the selected card on top.
  var deckEntries = [];
  var decks = Array.prototype.slice.call(
    document.querySelectorAll("[data-deck]")
  );

  decks.forEach(function (deck) {
    var cards = Array.prototype.slice.call(
      deck.querySelectorAll("[data-card]")
    );
    if (!cards.length) {
      return;
    }

    var selected = cards[0];
    var presented = cards[0];

    function updateStack() {
      var index = presented ? cards.indexOf(presented) : -1;
      var open = deck.classList.contains("is-open");
      var rank = 0;

      cards.forEach(function (card, position) {
        if (card === presented) {
          card.style.setProperty("--stack-rank", "0");
          card.style.zIndex = "60";
          return;
        }
        rank += 1;
        card.style.setProperty("--stack-rank", String(rank));
        card.style.zIndex = String(
          open
            ? index < 0
              ? position + 10
              : 50 - Math.abs(position - index)
            : 55 - rank
        );
      });
    }

    function applyPresentation(card) {
      presented = card;
      cards.forEach(function (other) {
        var active = other === card;
        other.classList.toggle("is-presented", active);
        other.setAttribute("aria-pressed", active ? "true" : "false");
      });
      updateStack();
    }

    function open() {
      deck.classList.add("is-open");
      if (!presented) {
        applyPresentation(selected);
      } else {
        updateStack();
      }
    }

    function close() {
      deck.classList.remove("is-open");
      if (selected) {
        applyPresentation(selected);
      } else {
        updateStack();
      }
    }

    deck.addEventListener("mouseenter", open);
    deck.addEventListener("mouseleave", close);

    deck.addEventListener("focusin", function (event) {
      var target = event.target;
      if (target.matches && target.matches(":focus-visible")) {
        open();
      }
    });

    deck.addEventListener("focusout", function (event) {
      if (!deck.contains(event.relatedTarget)) {
        close();
      }
    });

    cards.forEach(function (card) {
      card.addEventListener("click", function () {
        if (!deck.classList.contains("is-open")) {
          open();
          selected = card;
          applyPresentation(card);
          return;
        }
        if (card === presented) {
          if (cards.length > 1) {
            presented = null;
            cards.forEach(function (other) {
              other.classList.remove("is-presented");
              other.setAttribute("aria-pressed", "false");
            });
            updateStack();
          }
          return;
        }
        selected = card;
        applyPresentation(card);
      });
    });

    applyPresentation(presented);
    deckEntries.push({ deck: deck, close: close });
  });

  if (deckEntries.length) {
    document.addEventListener("pointerdown", function (event) {
      deckEntries.forEach(function (entry) {
        if (!entry.deck.contains(event.target)) {
          entry.close();
        }
      });
    });
  }

  // Rescue stills: the photos are a pile. Pressing the presented photo moves
  // to the next one, wrapping at the end; pressing a peeking card presents it.
  var reels = Array.prototype.slice.call(
    document.querySelectorAll("[data-reel]")
  );

  reels.forEach(function (reel) {
    var cards = Array.prototype.slice.call(
      reel.querySelectorAll("[data-reel-card]")
    );
    if (!cards.length) {
      return;
    }

    var presented = cards[0];

    function updateStack() {
      var index = cards.indexOf(presented);
      cards.forEach(function (card, position) {
        var depth = (position - index + cards.length) % cards.length;
        card.style.setProperty("--depth", String(depth));
        card.style.zIndex = String(cards.length - depth);
        card.classList.toggle("is-presented", depth === 0);
        card.setAttribute("aria-pressed", depth === 0 ? "true" : "false");
        card.tabIndex = depth === 0 ? 0 : -1;
      });
    }

    cards.forEach(function (card) {
      card.addEventListener("click", function () {
        if (card === presented) {
          presented = cards[(cards.indexOf(card) + 1) % cards.length];
        } else {
          presented = card;
        }
        updateStack();
      });
    });

    updateStack();
  });

  // YouTube refuses to configure a player without an HTTP referrer, so file://
  // previews keep the link behaviour and open the watch page instead. Over
  // HTTP(S) the click swaps the thumbnail for an inline player.
  var talkVideos = document.querySelectorAll("[data-embed]");
  talkVideos.forEach(function (link) {
    link.addEventListener("click", function (event) {
      if (window.location.protocol === "file:") {
        return;
      }
      event.preventDefault();

      var iframe = document.createElement("iframe");
      iframe.src = link.getAttribute("data-embed") + "?autoplay=1&rel=0";
      iframe.title = link.getAttribute("data-title") || "Talk video";
      iframe.allow = "autoplay; encrypted-media; picture-in-picture";
      iframe.allowFullscreen = true;
      link.replaceWith(iframe);
    });
  });
})();
