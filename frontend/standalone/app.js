const apiBaseUrl = "http://127.0.0.1:8000/api";
const userIdKey = "health-one-user-id";

const messageInput = document.querySelector("#messageInput");
const form = document.querySelector("#chatForm");
const submitButton = document.querySelector("#submitButton");
const resultRoot = document.querySelector("#resultRoot");
const errorBox = document.querySelector("#errorBox");

function getUserId() {
  const existing = localStorage.getItem(userIdKey);
  if (existing) return existing;

  const id = crypto.randomUUID();
  localStorage.setItem(userIdKey, id);
  return id;
}

if (window.location.hash && !document.querySelector(window.location.hash)) {
  history.replaceState(null, "", window.location.pathname);
  window.scrollTo({ top: 0 });
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const message = messageInput.value.trim();
  if (!message) {
    errorBox.hidden = false;
    errorBox.textContent = "请先输入饮食需求、食材或健康约束。";
    return;
  }

  submitButton.disabled = true;
  submitButton.textContent = "生成中...";
  errorBox.hidden = true;

  try {
    const response = await fetch(`${apiBaseUrl}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        user_id: getUserId(),
        message,
      }),
    });

    if (!response.ok) {
      throw new Error(`后端请求失败：${response.status}`);
    }

    const data = await response.json();
    renderResult(data);
  } catch (error) {
    errorBox.hidden = false;
    errorBox.textContent = error instanceof Error ? error.message : "请求失败";
  } finally {
    submitButton.disabled = false;
    submitButton.textContent = "生成推荐";
  }
});

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function nutritionMetrics(item) {
  return `
    <div class="metrics">
      <div><span>${item.calories}</span><small>kcal</small></div>
      <div><span>${item.protein_g}g</span><small>蛋白质</small></div>
      <div><span>${item.carbs_g}g</span><small>碳水</small></div>
      <div><span>${item.fat_g}g</span><small>脂肪</small></div>
      <div><span>${item.sodium_mg}mg</span><small>钠</small></div>
    </div>
  `;
}

function renderResult(data) {
  const contextRows = Object.entries(data.parsed_context)
    .map(([key, value]) => {
      const text = Array.isArray(value) ? value.join("、") : value ?? "未识别";
      return `<div><dt>${escapeHtml(key)}</dt><dd>${escapeHtml(text)}</dd></div>`;
    })
    .join("");

  const shopping = data.shopping_list.length
    ? data.shopping_list
        .map((item) => `<li><span>${escapeHtml(item.name)}</span><b>${item.amount_g}g</b></li>`)
        .join("")
    : `<p class="muted">当前库存足够，不需要额外购买。</p>`;

  const recipes = data.recipes
    .map((candidate) => {
      const recipe = candidate.recipe;
      const tags = recipe.taste_tags.map((tag) => `<span>${escapeHtml(tag)}</span>`).join("");
      const matched = candidate.matched_ingredients.join("、") || "暂无";
      const missing = candidate.missing_ingredients.map((item) => item.name).join("、") || "无需额外购买";
      const steps = recipe.steps.slice(0, 3).map((step) => `<li>${escapeHtml(step)}</li>`).join("");

      return `
        <article class="recipe-item">
          <header class="recipe-header">
            <div>
              <h3>${escapeHtml(recipe.name)}</h3>
              <p>${escapeHtml(recipe.cuisine)} / ${recipe.cooking_time_min} 分钟 / ${escapeHtml(recipe.difficulty)}</p>
            </div>
            <strong>${candidate.score}</strong>
          </header>
          <div class="tags">${tags}</div>
          ${nutritionMetrics(candidate.nutrition)}
          <div class="split">
            <p><b>已有：</b>${escapeHtml(matched)}</p>
            <p><b>缺少：</b>${escapeHtml(missing)}</p>
          </div>
          <ol>${steps}</ol>
        </article>
      `;
    })
    .join("");

  const warnings = data.warnings.map((warning) => `<li>${escapeHtml(warning)}</li>`).join("");

  resultRoot.hidden = false;
  resultRoot.innerHTML = `
    <section class="panel answer-panel">
      <p class="eyebrow">Agent 输出</p>
      <h2>推荐摘要</h2>
      <pre>${escapeHtml(data.answer)}</pre>
      ${nutritionMetrics(data.nutrition_summary)}
    </section>

    <section class="grid-two">
      <div class="panel">
        <p class="eyebrow">解析结果</p>
        <h2>识别到的约束</h2>
        <dl class="context-list">${contextRows}</dl>
      </div>

      <div id="shopping" class="panel">
        <p class="eyebrow">Shopping</p>
        <h2>购物清单</h2>
        <ul class="shopping-list">${shopping}</ul>
      </div>
    </section>

    <section id="recipes" class="recipe-list">${recipes}</section>

    <section class="panel">
      <p class="eyebrow">Safety</p>
      <h2>饮食提醒</h2>
      <ul class="warnings">${warnings}</ul>
    </section>
  `;

  if (window.location.hash) {
    document.querySelector(window.location.hash)?.scrollIntoView({ block: "start" });
  }
}
