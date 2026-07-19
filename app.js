

(function() {
// ── 主题切换 ──────────────────────────────────────
  var themeSwitch = document.getElementById("themeSwitch");
  var themeIcon = document.getElementById("themeIcon");
  var savedTheme = localStorage.getItem("notes-theme") || "light";
  document.documentElement.setAttribute("data-theme", savedTheme);
  updateSwitchState(savedTheme);

  function updateSwitchState(theme) {
    if (themeIcon) {
      themeIcon.src = theme === "dark" ? iconPath("moon.svg") : iconPath("sun.svg");
      themeIcon.alt = theme === "dark" ? "夜间模式" : "日间模式";
    }
    if (themeSwitch) {
      themeSwitch.setAttribute("aria-checked", theme === "dark" ? "true" : "false");
    }
  }

  // 根据当前页面位置计算图标路径
  function iconPath(name) {
    var path = window.location.pathname;
    if (path.indexOf("/notes/") !== -1) {
      return "../icon/" + name;
    }
    return "icon/" + name;
  }

  if (themeSwitch) {
    themeSwitch.addEventListener("click", function() {
      var current = document.documentElement.getAttribute("data-theme");
      var next = current === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", next);
      localStorage.setItem("notes-theme", next);
      updateSwitchState(next);
    });

    themeSwitch.addEventListener("keydown", function(e) {
      if (e.key === " " || e.key === "Enter") {
        e.preventDefault();
        this.click();
      }
    });
  }


  // ── 侧边栏折叠 ────────────────────────────────
  var sidebarToggle = document.getElementById("sidebarToggle");
  var sidebar = document.getElementById("sidebar");
  var overlay = document.getElementById("sidebarOverlay");
  var isMobile = window.innerWidth <= 768;

  // 移动端默认收起，桌面端记住偏好
  var savedCollapsed = localStorage.getItem("notes-sidebar-collapsed");
  if (savedCollapsed === "true" || (isMobile && savedCollapsed !== "false")) {
    document.body.classList.add("sidebar-collapsed");
    document.body.classList.remove("sidebar-open");
  }

  function toggleSidebar() {
    if (isMobile) {
      // 移动端：展开/收起覆盖层
      if (document.body.classList.contains("sidebar-open")) {
        document.body.classList.remove("sidebar-open");
      } else {
        document.body.classList.add("sidebar-open");
      }
      document.body.classList.remove("sidebar-collapsed");
    } else {
      // 桌面端：折叠/展开
      document.body.classList.toggle("sidebar-collapsed");
      document.body.classList.remove("sidebar-open");
      var collapsed = document.body.classList.contains("sidebar-collapsed");
      localStorage.setItem("notes-sidebar-collapsed", collapsed ? "true" : "false");
    }
  }

  if (sidebarToggle) {
    sidebarToggle.addEventListener("click", toggleSidebar);
  }

  // ── 侧边栏内部折叠按钮 ──────────────────────────
  var sidebarCollapseBtn = document.getElementById("sidebarCollapseBtn");
  if (sidebarCollapseBtn) {
    sidebarCollapseBtn.addEventListener("click", toggleSidebar);
  }

  if (overlay) {
    overlay.addEventListener("click", function() {
      document.body.classList.remove("sidebar-open");
    });
  }

  window.addEventListener("resize", function() {
    var wasMobile = isMobile;
    isMobile = window.innerWidth <= 768;
    if (wasMobile !== isMobile) {
      document.body.classList.remove("sidebar-open");
      if (!isMobile) {
        var c = localStorage.getItem("notes-sidebar-collapsed");
        if (c === "true") document.body.classList.add("sidebar-collapsed");
        else document.body.classList.remove("sidebar-collapsed");
      }
    }
  });

  // ── 搜索 ──────────────────────────────────────
  var search = document.getElementById("search");
  if (search) {
    search.addEventListener("input", function() {
      var q = this.value.toLowerCase();
      var grid = document.getElementById("noteGrid");
      var list = document.getElementById("noteList");
      if (grid) {
        grid.querySelectorAll(".note-card").forEach(function(c) {
          var title = (c.querySelector("h3") || {}).textContent || "";
          var excerpt = (c.querySelector("p") || {}).textContent || "";
          c.style.display = (title + excerpt).toLowerCase().includes(q) ? "" : "none";
        });
      }
      if (list) {
        list.querySelectorAll("li").forEach(function(li) {
          li.style.display = li.textContent.toLowerCase().includes(q) ? "" : "none";
        });
      }
    });
  }
  // ── 封面交互 ──────────────────────────────────
    var cover = document.getElementById("cover");
  if (cover) {
    var bgImages = [
      "icon/bg1.png",
      "icon/bg2.png",
      "icon/bg3.png",
      "icon/bg4.png",
      "icon/bg5.png"
    ];
    var randomBg = bgImages[Math.floor(Math.random() * bgImages.length)];

    cover.style.backgroundImage = 'url("' + randomBg + '")';
    cover.style.backgroundSize = 'cover';
    cover.style.backgroundPosition = 'center';
    cover.style.backgroundRepeat = 'no-repeat';

  }
  // 流星生成器
  (function() {
    var container = document.getElementById("coverStars");
    if (!container) return;
    function spawn() {
      var star = document.createElement("div");
      star.className = "cover-star";
      var top = Math.random() * 25;
      var left = 70 + Math.random() * 25;
      star.style.top = top + "%";
      star.style.left = left + "%";
      var dur = 2 + Math.random() * 0.6;
      star.style.setProperty("--dur", dur + "s");
      container.appendChild(star);
      setTimeout(function() { if (star.parentNode) star.parentNode.removeChild(star); }, dur * 1000 + 200);
    }
    function schedule() {
      spawn();
      setTimeout(schedule, 3000 + Math.random() * 1000);
    }
    setTimeout(schedule, 1500);
  })();

  var coverBtn = document.getElementById("coverBtn");

  // 封面标题逐字动画
    // 封面标题逐字动画（随机选择）
  var titleEl = document.getElementById("coverTitleText");
  if (titleEl) {
    // ── 预设标题列表（可自由增删） ──
    var quotes = [
      "循此苦旅，以抵繁星~",
      "学无止境，行以致远~",
      "千里之行，始于足下~"
    ];
    var randomIndex = Math.floor(Math.random() * quotes.length);
    var titleText = quotes[randomIndex];

    // 逐字动画（与原逻辑完全一致）
    var chars = titleText.split("");
    var totalDelay = 0;
    chars.forEach(function(ch, i) {
      var span = document.createElement("span");
      span.className = "cover-title-char";
      span.textContent = ch;
      var delay = 0.6 + i * 0.08;
      span.style.animationDelay = delay + "s";
      titleEl.appendChild(span);
      totalDelay = delay + 0.35;
    });
    var star = document.createElement("span");
    star.className = "cover-star-emoji";
    star.textContent = "⭐";
    star.style.setProperty("--star-delay", (totalDelay + 0.15) + "s");
    titleEl.appendChild(star);
  }

  // 进入笔记列表页
  function goToHome() {
    smoothNavigate("home.html");
  }

  if (coverBtn) {
    coverBtn.addEventListener("click", function(e) {
      e.preventDefault();
      goToHome();
    });
  }

  if (cover) {
    cover.addEventListener("wheel", function(e) {
      if (e.deltaY > 0) {
        goToHome();
      }
    }, { passive: true });
  }

  // 下滑箭头点击进入
  var scrollHint = document.getElementById("coverScrollHint");
  if (scrollHint) {
    scrollHint.addEventListener("click", function(e) {
      e.preventDefault();
      goToHome();
    });
  }

  // ── TOC 点击平滑滚动 ────────────────────────────
  var tocLinks = document.querySelectorAll(".toc-link");
  tocLinks.forEach(function(link) {
    link.addEventListener("click", function(e) {
      e.preventDefault();
      var targetId = this.getAttribute("href").substring(1);
      var target = document.getElementById(targetId);
      if (target) {
        target.scrollIntoView({ behavior: "smooth" });
        if (window.innerWidth <= 768) {
          document.body.classList.remove("sidebar-open");
        }
      }
    });
  });

  // ═══════════════════════════════════════════════════════
  // ★ 新增：TOC 滚动高亮当前阅读位置
  // ═══════════════════════════════════════════════════════
  function initTocHighlight() {
    var tocLinks = document.querySelectorAll('.toc-link');
    if (tocLinks.length === 0) return;

    // 收集标题元素与其对应的 TOC 链接
    var headingMap = [];
    tocLinks.forEach(function(link) {
      var targetId = link.getAttribute('href').substring(1);
      var heading = document.getElementById(targetId);
      if (heading) {
        headingMap.push({
          heading: heading,
          link: link
        });
      }
    });

    if (headingMap.length === 0) return;

    // 使用 Intersection Observer 检测标题进入视口
    var observer = new IntersectionObserver(function(entries) {
      // 收集当前可见的标题（至少 30% 可见）
      var visibleHeadings = entries
        .filter(function(entry) {
          return entry.isIntersecting && entry.intersectionRatio >= 0.3;
        })
        .map(function(entry) {
          return entry.target;
        });

      if (visibleHeadings.length === 0) {
        // 如果没有标题可见（滚动到顶部或底部），则根据滚动位置选择最接近的
        var scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        var closest = null;
        var minDist = Infinity;
        headingMap.forEach(function(item) {
          var rect = item.heading.getBoundingClientRect();
          var dist = Math.abs(rect.top);
          if (dist < minDist) {
            minDist = dist;
            closest = item;
          }
        });
        if (closest) {
          setActiveLink(closest.link);
        }
        return;
      }

      // 选择第一个可见标题（按 DOM 顺序）
      var firstVisible = visibleHeadings[0];
      var activeItem = null;
      for (var i = 0; i < headingMap.length; i++) {
        if (headingMap[i].heading === firstVisible) {
          activeItem = headingMap[i];
          break;
        }
      }
      if (activeItem) {
        setActiveLink(activeItem.link);
      }
    }, {
      threshold: [0.3, 0.5, 0.7],
      rootMargin: '0px 0px -10% 0px'
    });

    headingMap.forEach(function(item) {
      observer.observe(item.heading);
    });

    // 初始高亮
    requestAnimationFrame(function() {
      var scrollTop = window.pageYOffset || document.documentElement.scrollTop;
      var activeItem = null;
      for (var i = 0; i < headingMap.length; i++) {
        var rect = headingMap[i].heading.getBoundingClientRect();
        if (rect.top >= 0 && rect.top < window.innerHeight * 0.7) {
          activeItem = headingMap[i];
          break;
        }
      }
      if (!activeItem && headingMap.length > 0) {
        activeItem = headingMap[headingMap.length - 1];
      }
      if (activeItem) {
        setActiveLink(activeItem.link);
      }
    });

    function setActiveLink(activeLink) {
      tocLinks.forEach(function(link) {
        link.classList.remove('active');
      });
      activeLink.classList.add('active');
    }
  }

  // 在页面加载完成后初始化
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initTocHighlight);
  } else {
    initTocHighlight();
  }
  // ═══════════════════════════════════════════════════════

  // ── 侧边栏返回键 → 笔记列表页 ─────────────────
  var sidebarBack = document.getElementById("sidebarBack");
  if (sidebarBack) {
    sidebarBack.addEventListener("click", function(e) {
      e.preventDefault();
      var path = window.location.pathname;
      var homeHref = path.indexOf("/notes/") !== -1 ? "../home.html" : "home.html";
      smoothNavigate(homeHref);
    });
  }

  // ── 首页按钮（右上角小房子）───────────────────
  var homeBtn = document.getElementById("homeBtn");
  if (homeBtn) {
    homeBtn.addEventListener("click", function(e) {
      e.preventDefault();
      var href = this.getAttribute("href");
      smoothNavigate(href);
    });
  }

  function smoothNavigate(href) {
    document.body.classList.add("page-out");
    setTimeout(function() {
      window.location.href = href;
    }, 200);
  }

  var noteCards = document.querySelectorAll(".note-card");
  noteCards.forEach(function(card) {
    card.addEventListener("click", function(e) {
      var href = this.getAttribute("href");
      if (href && href !== "#" && href !== window.location.href) {
        e.preventDefault();
        smoothNavigate(href);
      }
    });
  });

  var noteListLinks = document.querySelectorAll("#noteList a");
  noteListLinks.forEach(function(link) {
    link.addEventListener("click", function(e) {
      var href = this.getAttribute("href");
      if (href && href !== "#" && href !== window.location.href) {
        e.preventDefault();
        smoothNavigate(href);
      }
    });
  });

  var sidebarNavLinks = document.querySelectorAll("#sidebarNav a");
  sidebarNavLinks.forEach(function(link) {
    link.addEventListener("click", function(e) {
      var href = this.getAttribute("href");
      if (href && href !== "#" && href !== window.location.href) {
        e.preventDefault();
        smoothNavigate(href);
      }
    });
  });

})();

