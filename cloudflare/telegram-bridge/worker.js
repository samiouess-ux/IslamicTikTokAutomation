const WORKFLOW_FILE = "telegram-quran-request.yml";
const TARGET_BRANCH = "feature/telegram-review-notifications";

async function telegramMessage(env, chatId, text) {
  const response = await fetch(`https://api.telegram.org/bot${env.TELEGRAM_BOT_TOKEN}/sendMessage`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ chat_id: chatId, text }),
  });
  if (!response.ok) throw new Error(`Telegram sendMessage HTTP ${response.status}`);
  const result = await response.json();
  if (!result.ok) throw new Error("Telegram rejected sendMessage");
}

export default {
  async fetch(request, env) {
    if (request.method !== "POST") {
      return new Response("Method not allowed", { status: 405 });
    }

    const suppliedSecret = request.headers.get("X-Telegram-Bot-Api-Secret-Token") || "";
    if (!env.TELEGRAM_WEBHOOK_SECRET || suppliedSecret !== env.TELEGRAM_WEBHOOK_SECRET) {
      return new Response("Unauthorized", { status: 401 });
    }

    let update;
    try {
      update = await request.json();
    } catch {
      return new Response("Bad request", { status: 400 });
    }

    const message = update.message || update.edited_message;
    if (!message || typeof message.text !== "string" || !message.chat) {
      return new Response("Ignored", { status: 200 });
    }

    const chatId = String(message.chat.id);
    if (!env.ALLOWED_TELEGRAM_CHAT_ID || chatId !== String(env.ALLOWED_TELEGRAM_CHAT_ID)) {
      return new Response("Ignored", { status: 200 });
    }

    const requestText = message.text.trim();
    if (!requestText || requestText.length > 300 || /[\r\n]/.test(requestText)) {
      await telegramMessage(
        env,
        chatId,
        "ابعث طلب في سطر واحد، مثال: فيديو سورة الكهف الآيات 1-5"
      );
      return new Response("Invalid request text", { status: 200 });
    }

    const updateId = Number(update.update_id);
    if (!Number.isSafeInteger(updateId) || updateId < 0) {
      return new Response("Invalid update id", { status: 400 });
    }
    if (!env.TELEGRAM_UPDATES) {
      return new Response("Dedupe KV binding is missing", { status: 503 });
    }

    const dedupeKey = `telegram-update-${updateId}`;
    const alreadySeen = await env.TELEGRAM_UPDATES.get(dedupeKey);
    if (alreadySeen) {
      return new Response("Duplicate update", { status: 200 });
    }

    // Reserve before dispatch so a Telegram retry cannot normally enqueue a
    // second workflow. Remove the reservation if GitHub rejects the dispatch.
    await env.TELEGRAM_UPDATES.put(dedupeKey, "dispatching", { expirationTtl: 604800 });

    const repository = env.GITHUB_REPOSITORY || "samiouess-ux/IslamicTikTokAutomation";
    const dispatchUrl = `https://api.github.com/repos/${repository}/actions/workflows/${WORKFLOW_FILE}/dispatches`;
    let dispatchResponse;
    try {
      dispatchResponse = await fetch(dispatchUrl, {
        method: "POST",
        headers: {
          "accept": "application/vnd.github+json",
          "authorization": `Bearer ${env.GITHUB_TOKEN}`,
          "x-github-api-version": "2022-11-28",
          "content-type": "application/json",
          "user-agent": "IslamicTikTokAutomation-Telegram-Bridge",
        },
        body: JSON.stringify({
          ref: TARGET_BRANCH,
          inputs: { request_text: requestText },
        }),
      });
    } catch (error) {
      await env.TELEGRAM_UPDATES.delete(dedupeKey);
      return new Response("GitHub dispatch network error", { status: 502 });
    }

    if (dispatchResponse.status !== 204) {
      await env.TELEGRAM_UPDATES.delete(dedupeKey);
      return new Response("GitHub rejected workflow dispatch", { status: 502 });
    }

    await env.TELEGRAM_UPDATES.put(dedupeKey, "dispatched", { expirationTtl: 604800 });

    try {
      await telegramMessage(
        env,
        chatId,
        "وصل طلبك ✅ نحضّر المقطع للمراجعة. نبعثهولك هنا كي يكمل. النشر على TikTok يبقى يدوي."
      );
    } catch {
      // The workflow has already been queued; do not return an error that
      // would make Telegram retry and potentially enqueue the same request.
    }

    return new Response("Accepted", { status: 200 });
  },
};
