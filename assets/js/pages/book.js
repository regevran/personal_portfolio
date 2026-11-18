/* Book page behavior.
   Page-turn engine: pdflip 0.1.0 (BSD-3-Clause), built on pdf.js.
   https://github.com/WapplerSystems/pdflip — see the vendored licenses. */
(function () {
  "use strict";

  var viewer = document.querySelector("[data-book]");
  if (!viewer) {
    return;
  }

  var element = viewer.querySelector("[data-book-pdf]");
  var source = viewer.getAttribute("data-book-source");
  if (!element || !source) {
    return;
  }
  if (!window.Pdflip) {
    viewer.classList.add("book-viewer--failed");
    return;
  }

  var counter = viewer.querySelector("[data-book-counter]");
  var next = viewer.querySelector("[data-book-next]");
  var previous = viewer.querySelector("[data-book-prev]");
  var form = viewer.querySelector("[data-book-goto]");
  var input = viewer.querySelector("[data-book-goto-input]");
  var offset = parseInt(viewer.getAttribute("data-book-page-offset"), 10);
  var numberedPages = parseInt(
    viewer.getAttribute("data-book-numbered-pages"),
    10
  );
  var ready = false;
  var book;

  if (!isFinite(offset) || offset < 0) {
    offset = 0;
  }
  if (!isFinite(numberedPages) || numberedPages < 1) {
    numberedPages = 0;
  }

  try {
    book = new window.Pdflip.Flipbook(element, {
      source: source,
      direction: "rtl",
      flipStyle: "cover",
      pageMode: "auto",
      controls: [],
      duration: 700,
      pdfjs: { disableRange: true }
    });
  } catch (error) {
    viewer.classList.add("book-viewer--failed");
    return;
  }

  function renderedPdfPages() {
    var rendered = [];
    var nodes = element.querySelectorAll(".pdflip-page[aria-label]");
    for (var index = 0; index < nodes.length; index += 1) {
      var match = /^Page (\d+)$/.exec(
        nodes[index].getAttribute("aria-label") || ""
      );
      if (match) {
        rendered.push(parseInt(match[1], 10));
      }
    }
    return rendered;
  }

  function visiblePdfPages(pages) {
    var visible = [];
    var pageList = pages && pages.length ? pages : renderedPdfPages();
    for (var index = 0; index < pageList.length; index += 1) {
      var value = parseInt(pageList[index], 10);
      if (isFinite(value)) {
        visible.push(value);
      }
    }
    if (!visible.length) {
      visible.push(book.page);
    }
    visible.sort(function (a, b) {
      return a - b;
    });
    return visible;
  }

  function printedPage(pdfPage) {
    if (!numberedPages) {
      return null;
    }
    var printed = pdfPage - offset;
    return printed >= 1 && printed <= numberedPages ? printed : null;
  }

  function unnumberedLabel(pdfPage, total) {
    if (pdfPage <= 1) {
      return "Cover";
    }
    if (total && pdfPage >= total) {
      return "Back cover";
    }
    if (pdfPage > offset + numberedPages) {
      return "Blank page";
    }
    return "Front matter";
  }

  function update(pages) {
    var page = book.page;
    var total = book.pageCount || 0;
    var visible = visiblePdfPages(pages);
    var printed = [];
    var labels = [];
    var index;

    for (index = 0; index < visible.length; index += 1) {
      var printedValue = printedPage(visible[index]);
      if (printedValue !== null && printed.indexOf(printedValue) === -1) {
        printed.push(printedValue);
      }
    }

    if (counter) {
      if (printed.length === 1) {
        counter.textContent =
          "Page " + printed[0] + " of " + numberedPages;
      } else if (printed.length > 1) {
        counter.textContent =
          "Pages " + printed[0] + "–" +
          printed[printed.length - 1] + " of " + numberedPages;
      } else if (numberedPages) {
        for (index = 0; index < visible.length; index += 1) {
          var label = unnumberedLabel(visible[index], total);
          if (labels.indexOf(label) === -1) {
            labels.push(label);
          }
        }
        if (labels.length === 1 && labels[0] === "Blank page" &&
            visible.length > 1) {
          counter.textContent = "Blank pages";
        } else {
          counter.textContent = labels.join(" · ");
        }
      } else if (page <= 1) {
        counter.textContent = "Cover";
      } else if (visible.length > 1) {
        counter.textContent =
          "Pages " + visible[0] + "–" +
          visible[visible.length - 1] + " of " + total;
      } else {
        counter.textContent = "Page " + visible[0] + " of " + total;
      }
    }

    if (previous) {
      previous.disabled = !ready || page <= 1;
    }
    if (next) {
      next.disabled = !ready || page >= total;
    }
    if (input) {
      input.max = numberedPages || total || "";
      input.disabled = !ready;
    }
  }

  function turn(forward) {
    if (forward) {
      book.next();
    } else {
      book.prev();
    }
  }

  if (next) {
    next.addEventListener("click", function () {
      turn(true);
    });
  }
  if (previous) {
    previous.addEventListener("click", function () {
      turn(false);
    });
  }
  if (form && input) {
    form.addEventListener("submit", function (event) {
      event.preventDefault();
      var target = parseInt(input.value, 10);
      var limit = numberedPages || book.pageCount;
      if (!isFinite(target) || !limit) {
        input.focus();
        return;
      }
      target = Math.min(Math.max(target, 1), limit);
      var physical = numberedPages ? target + offset : target;
      if (book.pageCount) {
        physical = Math.min(Math.max(physical, 1), book.pageCount);
      }
      book.goTo(physical);
      input.value = "";
      input.blur();
    });
  }

  book.on("flip", function (event) {
    update(event.pages);
  });
  book.on("ready", function () {
    ready = true;
    update();
  });
  book.on("error", function () {
    viewer.classList.add("book-viewer--failed");
  });

  var resizeTimer;
  window.addEventListener("resize", function () {
    if (resizeTimer) {
      clearTimeout(resizeTimer);
    }
    resizeTimer = setTimeout(function () {
      update();
    }, 250);
  });

  update([book.page]);
})();
