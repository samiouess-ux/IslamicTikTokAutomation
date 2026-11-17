"use client";

import { useCallback, useEffect, useState } from "react";

const dateFormat = new Intl.DateTimeFormat("ar-TN", {
  dateStyle: "medium",
  timeStyle: "short"
});

function formatDate(value) {
  if (!value) return "—";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? "—" : dateFormat.format(date);
}

function runLabel(run) {
  if (run.status === "in_progress" || run.status === "queued") return "قيد التنفيذ";
  if (run.conclusion === "success") return "ناجح";
  if (run.conclusion === "failure") return "فشل";
  if (run.conclusion === "cancelled") return "أُلغي";
  return run.conclusion || run.status || "غير معروف";
}

export default function Dashboard() {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState(null);

  const refresh = useCallback(async () => {
    try {
      const response = await fetch("/api/dashboard", { cache: "no-store" });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.error || "تعذّر تحميل البيانات.");
      setData(payload);
      setError("");
      setLastUpdated(new Date());
    } catch (err) {
      setError(err.message || "صار خطأ غير متوقّع.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
    const timer = setInterval(refresh, 60000);
    return () => clearInterval(timer);
  }, [refresh]);

  return (
    <main className="shell">
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark">۞</div>
          <div>
            <div className="brand-name">QURAN STUDIO</div>
            <div className="brand-subtitle">لوحة المتابعة الخاصة</div>
          </div>
        </div>
        <span className="private-pill"><span className="live-dot" /> خاصة</span>
      </header>

      <section className="hero">
        <div className="eyebrow">مساحة الإدارة الشخصية</div>
        <h1>السلام عليكم 👋</h1>
        <p>كل حالة المحرك في بلاصة واحدة. متابعة فقط، من غير ما نبدّلوا طريقة الإنتاج.</p>
        <div className="hero-meta">
          <span>● مراقبة مباشرة</span>
          <span>تحديث كل دقيقة</span>
        </div>
      </section>

      {error && (
        <div className="error-panel" role="alert">
          <strong>تعذّر تحديث البيانات</strong>
          <p>{error}</p>
          <button className="secondary-button" onClick={refresh}>عاود المحاولة</button>
        </div>
      )}

      <section className="section-heading">
        <div><span className="section-kicker">OVERVIEW</span><h2>نظرة عامة</h2></div>
        <button className="refresh-button" onClick={refresh} disabled={loading}>↻ تحديث</button>
      </section>

      <section className="stats-grid">
        <StatCard icon="▶" label="تسليمات مسجّلة" value={data?.stats.deliveries} hint="في سجلّ التسليم" />
        <StatCard icon="۞" label="آيات مسجّلة" value={data?.stats.ayahs} hint="تم تفادي تكرارها" />
        <StatCard icon="▧" label="كل الخلفيات" value={data?.stats.backgrounds} hint="في الكاتالوغ" />
        <StatCard icon="✦" label="خلفيات التدوير" value={data?.stats.eligibleBackgrounds} hint="موافقة + تحقق" />
      </section>

      <section className="content-grid">
        <div className="panel">
          <div className="panel-heading">
            <div><span className="section-kicker">AUTOMATION</span><h2>آخر العمليات</h2></div>
            <span className="subtle-count">{data?.runs?.length ?? "—"} عمليات</span>
          </div>
          {loading && !data ? <EmptyState>نحمّل بيانات GitHub…</EmptyState> :
            data?.runs?.length ? (
              <div className="run-list">
                {data.runs.map(run => (
                  <a className="run-row" href={run.url} target="_blank" rel="noreferrer" key={run.id}>
                    <span className={`status-icon ${run.conclusion === "success" ? "good" : run.conclusion === "failure" ? "bad" : "neutral"}`}>
                      {run.conclusion === "success" ? "✓" : run.conclusion === "failure" ? "!" : "•"}
                    </span>
                    <span className="row-main">
                      <strong>{run.name || "GitHub Actions"}</strong>
                      <small>{run.event} · {formatDate(run.createdAt)}</small>
                    </span>
                    <span className={`status-label ${run.conclusion === "success" ? "good-text" : run.conclusion === "failure" ? "bad-text" : ""}`}>{runLabel(run)}</span>
                    <span className="arrow">↗</span>
                  </a>
                ))}
              </div>
            ) : <EmptyState>ما فماش عمليات ظاهرة في الفرع المحدّد.</EmptyState>}
        </div>

        <div className="panel">
          <div className="panel-heading">
            <div><span className="section-kicker">QURAN HISTORY</span><h2>آخر السور</h2></div>
          </div>
          {data?.latestDeliveries?.length ? (
            <div className="delivery-list">
              {data.latestDeliveries.map((item, index) => (
                <div className="delivery-row" key={item.candidate_id || index}>
                  <div className="surah-number">{item.surah_number ?? "۞"}</div>
                  <div className="row-main">
                    <strong>{item.candidate_id || "تسليم قرآني"}</strong>
                    <small>{item.selected_verses?.length || 0} آيات · {formatDate(item.delivered_at_utc)}</small>
                  </div>
                  <span className="delivery-check">✓</span>
                </div>
              ))}
            </div>
          ) : <EmptyState>سجلّ التسليم يظهر هنا.</EmptyState>}
        </div>
      </section>

      <section className="panel backgrounds-panel">
        <div className="panel-heading">
          <div><span className="section-kicker">VISUAL LIBRARY</span><h2>مكتبة الخلفيات</h2></div>
          <span className="subtle-count">{data?.stats.eligibleBackgrounds ?? "—"} مؤهّلة</span>
        </div>
        <div className="background-grid">
          {(data?.backgrounds || []).map(item => (
            <div className="background-card" key={item.id}>
              <div className={`background-symbol ${item.eligible ? "approved" : ""}`}>{item.eligible ? "✦" : "▧"}</div>
              <div className="background-info">
                <strong>{item.description}</strong>
                <small>{item.id}</small>
              </div>
              <span className={`background-state ${item.eligible ? "state-good" : "state-muted"}`}>
                {item.eligible ? "تدخل في التدوير" : "غير مؤهّلة"}
              </span>
            </div>
          ))}
        </div>
      </section>

      <footer className="footer">
        <span>Quran Studio · Private Monitor</span>
        <span>{lastUpdated ? `آخر تحديث: ${formatDate(lastUpdated)}` : "بانتظار البيانات"}</span>
      </footer>
    </main>
  );
}

function StatCard({ icon, label, value, hint }) {
  return (
    <article className="stat-card">
      <div className="stat-top"><span className="stat-icon">{icon}</span><span className="stat-accent" /></div>
      <div className="stat-value">{value === undefined ? "—" : Number(value).toLocaleString("ar-TN")}</div>
      <div className="stat-label">{label}</div>
      <div className="stat-hint">{hint}</div>
    </article>
  );
}

function EmptyState({ children }) {
  return <div className="empty-state">{children}</div>;
}
