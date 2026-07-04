import { FormEvent, useMemo, useState } from "react";
import { sendChat } from "./api/client";
import type { ChatResponse, RecipeCandidate } from "./types";

function NutritionLine({ item }: { item: ChatResponse["nutrition_summary"] }) {
  return (
    <div className="metrics">
      <div><span>{item.calories}</span><small>kcal</small></div>
      <div><span>{item.protein_g}g</span><small>蛋白质</small></div>
      <div><span>{item.carbs_g}g</span><small>碳水</small></div>
      <div><span>{item.fat_g}g</span><small>脂肪</small></div>
      <div><span>{item.sodium_mg}mg</span><small>钠</small></div>
    </div>
  );
}

function RecipeItem({ candidate }: { candidate: RecipeCandidate }) {
  const recipe = candidate.recipe;

  return (
    <article className="recipe-item">
      <header className="recipe-header">
        <div>
          <h3>{recipe.name}</h3>
          <p>{recipe.cuisine} / {recipe.cooking_time_min} 分钟 / {recipe.difficulty}</p>
        </div>
        <strong>{candidate.score}</strong>
      </header>

      <div className="tags">
        {recipe.taste_tags.map((tag) => <span key={tag}>{tag}</span>)}
      </div>

      <NutritionLine item={candidate.nutrition} />

      <div className="split">
        <p><b>已有：</b>{candidate.matched_ingredients.join("、") || "暂无"}</p>
        <p><b>缺少：</b>{candidate.missing_ingredients.map((item) => item.name).join("、") || "无需额外购买"}</p>
      </div>

      <ol>
        {recipe.steps.slice(0, 3).map((step) => <li key={step}>{step}</li>)}
      </ol>
    </article>
  );
}

export default function App() {
  const [message, setMessage] = useState("");
  const [result, setResult] = useState<ChatResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const parsedContext = useMemo(() => {
    if (!result) return [];
    return Object.entries(result.parsed_context).map(([key, value]) => ({
      key,
      value: Array.isArray(value) ? value.join("、") : String(value ?? "未识别"),
    }));
  }, [result]);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!message.trim()) {
      setError("请先输入饮食需求、食材或健康约束。");
      return;
    }

    setLoading(true);
    setError("");
    try {
      const response = await sendChat(message);
      setResult(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : "请求失败");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div>
          <p className="eyebrow">Health ONE</p>
          <h1>智能健康做菜助手</h1>
          <p className="summary">菜谱知识库、RAG 检索、DeepSeek Agent 工具调用、营养计算、慢病轻盐提醒和购物清单。</p>
        </div>
        <nav>
          <a href="#chat">对话</a>
          <a href="#recipes">推荐</a>
          <a href="#shopping">购物清单</a>
        </nav>
      </aside>

      <section className="workspace">
        <section id="chat" className="panel chat-panel">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">Agent 输入</p>
              <h2>今天想怎么吃？</h2>
            </div>
          </div>

          <form onSubmit={handleSubmit}>
            <textarea
              value={message}
              onChange={(event) => setMessage(event.target.value)}
              rows={6}
              placeholder="输入食材、训练、忌口、疾病约束和做饭时间"
            />
            <button type="submit" disabled={loading}>{loading ? "生成中..." : "生成推荐"}</button>
          </form>
          {error && <p className="error">{error}</p>}
        </section>

        {result && (
          <>
            <section className="panel answer-panel">
              <p className="eyebrow">Agent 输出</p>
              <h2>推荐摘要</h2>
              <pre>{result.answer}</pre>
              <NutritionLine item={result.nutrition_summary} />
            </section>

            <section className="grid-two">
              <div className="panel">
                <p className="eyebrow">解析结果</p>
                <h2>识别到的约束</h2>
                <dl className="context-list">
                  {parsedContext.map((item) => (
                    <div key={item.key}>
                      <dt>{item.key}</dt>
                      <dd>{item.value}</dd>
                    </div>
                  ))}
                </dl>
              </div>

              <div id="shopping" className="panel">
                <p className="eyebrow">Shopping</p>
                <h2>购物清单</h2>
                {result.shopping_list.length ? (
                  <ul className="shopping-list">
                    {result.shopping_list.map((item) => (
                      <li key={item.name}>
                        <span>{item.name}</span>
                        <b>{item.amount_g}g</b>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="muted">当前库存足够，不需要额外购买。</p>
                )}
              </div>
            </section>

            <section id="recipes" className="recipe-list">
              {result.recipes.map((candidate) => (
                <RecipeItem key={candidate.recipe.id} candidate={candidate} />
              ))}
            </section>

            <section className="panel">
              <p className="eyebrow">Safety</p>
              <h2>饮食提醒</h2>
              <ul className="warnings">
                {result.warnings.map((warning) => <li key={warning}>{warning}</li>)}
              </ul>
            </section>
          </>
        )}
      </section>
    </main>
  );
}
