(function () {
  var modal;
  var lastActiveElement;

  function focusSearchInput() {
    window.setTimeout(function () {
      var input = document.querySelector("#site-search input");
      if (input) input.focus();
    }, 40);
  }

  function openSearch() {
    modal = modal || document.querySelector("#search-modal");
    if (!modal) return;

    lastActiveElement = document.activeElement;
    modal.setAttribute("aria-hidden", "false");
    document.body.classList.add("search-modal-open");
    focusSearchInput();
  }

  function closeSearch() {
    modal = modal || document.querySelector("#search-modal");
    if (!modal || modal.getAttribute("aria-hidden") === "true") return;

    modal.setAttribute("aria-hidden", "true");
    document.body.classList.remove("search-modal-open");

    if (lastActiveElement && typeof lastActiveElement.focus === "function") {
      lastActiveElement.focus();
    }
  }

  function initSearchShell() {
    modal = document.querySelector("#search-modal");

    document.querySelectorAll("[data-search-open]").forEach(function (trigger) {
      trigger.addEventListener("click", openSearch);
    });

    document.querySelectorAll("[data-search-close]").forEach(function (trigger) {
      trigger.addEventListener("click", closeSearch);
    });

    document.addEventListener("keydown", function (event) {
      var isSearchShortcut = (event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k";
      if (isSearchShortcut) {
        event.preventDefault();
        openSearch();
        return;
      }

      if (event.key === "Escape") {
        closeSearch();
      }
    });
  }

  function initSearch() {
    var root = document.querySelector("#site-search");
    if (!root) return;

    if (!window.PagefindUI) {
      root.innerHTML = '<div class="search-unavailable">搜索索引尚未生成。部署或运行 <code>npm run build:search</code> 后即可使用。</div>';
      return;
    }

    new window.PagefindUI({
      element: "#site-search",
      baseUrl: "/ai-news/",
      showImages: false,
      showSubResults: true,
      excerptLength: 30,
      resetStyles: false,
      processResult: function (result) {
        return result;
      },
      translations: {
        placeholder: "搜索 Agent、模型、产品、论文、Builder...",
        clear_search: "清空",
        load_more: "加载更多结果",
        search_label: "站内搜索",
        filters_label: "筛选",
        zero_results: "没有找到结果",
        many_results: "[COUNT] 条结果",
        one_result: "[COUNT] 条结果",
        alt_search: "没有找到 [SEARCH_TERM]，改搜 [DIFFERENT_TERM]"
      }
    });
  }

  function initDailyMasonry() {
    document.querySelectorAll(".vlist-2col").forEach(function (list) {
      var items = Array.prototype.slice.call(list.children).filter(function (child) {
        return child.classList && child.classList.contains("vitem");
      });
      if (!items.length) return;

      var sourceOrder = items.slice();
      var mq = window.matchMedia("(max-width: 768px)");

      function restoreSingleColumn() {
        sourceOrder.forEach(function (item) {
          list.appendChild(item);
        });
        Array.prototype.slice.call(list.querySelectorAll(":scope > .masonry-column")).forEach(function (column) {
          column.remove();
        });
      }

      function buildMasonry() {
        if (mq.matches) {
          restoreSingleColumn();
          return;
        }

        restoreSingleColumn();
        var gap = 10;
        var measuredHeights = sourceOrder.map(function (item) {
          return item.getBoundingClientRect().height;
        });
        var columnIndexes = chooseColumnIndexes(measuredHeights, gap);
        var columns = [document.createElement("div"), document.createElement("div")];

        columns.forEach(function (column) {
          column.className = "masonry-column";
        });

        columnIndexes.forEach(function (indexes, columnIndex) {
          indexes.forEach(function (itemIndex) {
            columns[columnIndex].appendChild(sourceOrder[itemIndex]);
          });
        });

        list.replaceChildren(columns[0], columns[1]);
      }

      function chooseColumnIndexes(heights, gap) {
        if (heights.length > 18) return chooseGreedyColumnIndexes(heights, gap);

        var bestMask = 1;
        var bestDelta = Infinity;
        var bestBalance = Infinity;
        var limit = Math.pow(2, heights.length - 1);

        for (var partial = 0; partial < limit; partial += 1) {
          var mask = (partial << 1) | 1;
          var heightsByColumn = [0, 0];
          var counts = [0, 0];

          heights.forEach(function (height, index) {
            var columnIndex = mask & (1 << index) ? 0 : 1;
            heightsByColumn[columnIndex] += height;
            counts[columnIndex] += 1;
          });

          heightsByColumn[0] += Math.max(0, counts[0] - 1) * gap;
          heightsByColumn[1] += Math.max(0, counts[1] - 1) * gap;

          var delta = Math.abs(heightsByColumn[0] - heightsByColumn[1]);
          var balance = Math.abs(counts[0] - counts[1]);
          if (delta < bestDelta || (delta === bestDelta && balance < bestBalance)) {
            bestDelta = delta;
            bestBalance = balance;
            bestMask = mask;
          }
        }

        return indexesFromMask(heights, bestMask);
      }

      function chooseGreedyColumnIndexes(heights, gap) {
        var columns = [[], []];
        var totals = [0, 0];

        heights.forEach(function (height, index) {
          var columnIndex = totals[0] <= totals[1] ? 0 : 1;
          columns[columnIndex].push(index);
          totals[columnIndex] += height + (columns[columnIndex].length > 1 ? gap : 0);
        });

        return columns;
      }

      function indexesFromMask(heights, mask) {
        var columns = [[], []];
        heights.forEach(function (_height, index) {
          columns[mask & (1 << index) ? 0 : 1].push(index);
        });
        return columns;
      }

      buildMasonry();
      window.addEventListener("resize", buildMasonry, { passive: true });
      window.addEventListener("load", buildMasonry, { once: true });
      sourceOrder.forEach(function (item) {
        item.querySelectorAll("img").forEach(function (img) {
          if (!img.complete) img.addEventListener("load", buildMasonry, { once: true });
        });
      });
    });
  }

  function init() {
    initSearchShell();
    initDailyMasonry();
    initSearch();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
