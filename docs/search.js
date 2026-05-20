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

  function init() {
    initSearchShell();
    initSearch();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
