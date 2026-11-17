import { NextResponse } from "next/server";

export const dynamic = "force-dynamic";
export const revalidate = 0;

const OWNER = process.env.DASHBOARD_REPO_OWNER || "samiouess-ux";
const REPO = process.env.DASHBOARD_REPO_NAME || "IslamicTikTokAutomation";
const BRANCH = process.env.DASHBOARD_BRANCH || "feature/telegram-review-notifications";

async function github(path) {
  const token = process.env.GITHUB_READ_TOKEN;
  if (!token) throw new Error("GITHUB_READ_TOKEN غير مضبوط في إعدادات الاستضافة.");

  const response = await fetch(`https://api.github.com/repos/${OWNER}/${REPO}/${path}`, {
    headers: {
      Accept: "application/vnd.github+json",
      Authorization: `Bearer ${token}`,
      "X-GitHub-Api-Version": "2022-11-28"
    },
    cache: "no-store"
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`GitHub API (${response.status}): ${detail.slice(0, 240)}`);
  }
  return response.json();
}

async function readJsonFile(path) {
  const file = await github(`contents/${path}?ref=${encodeURIComponent(BRANCH)}`);
  if (!file.content) throw new Error(`الملف فارغ أو غير قابل للقراءة: ${path}`);
  return JSON.parse(Buffer.from(file.content, "base64").toString("utf8"));
}

export async function GET() {
  try {
    const [history, catalog, runs] = await Promise.all([
      readJsonFile("data/quran_delivery_history.json"),
      readJsonFile("data/background_candidates.json"),
      github(`actions/runs?branch=${encodeURIComponent(BRANCH)}&per_page=8`)
    ]);

    const candidates = Array.isArray(catalog.candidates) ? catalog.candidates : [];
    const eligible = candidates.filter(item =>
      item.approved === true &&
      item.user_approved === true &&
      item.download_verified === true &&
      item.aspect_ratio === "9:16" &&
      typeof item.direct_video_url === "string" &&
      item.direct_video_url.startsWith("https://") &&
      typeof item.source_page_url === "string" &&
      item.source_page_url.startsWith("https://")
    );

    const deliveries = Array.isArray(history.deliveries) ? history.deliveries : [];
    const workflowRuns = Array.isArray(runs.workflow_runs) ? runs.workflow_runs : [];

    return NextResponse.json({
      updatedAt: new Date().toISOString(),
      branch: BRANCH,
      stats: {
        deliveries: deliveries.length,
        ayahs: Array.isArray(history.ayah_references) ? history.ayah_references.length : 0,
        backgrounds: candidates.length,
        eligibleBackgrounds: eligible.length
      },
      latestDeliveries: deliveries.slice(-8).reverse(),
      backgrounds: candidates.map(item => ({
        id: item.id,
        description: item.description || item.title || item.id,
        approved: item.approved === true && item.user_approved === true,
        eligible: eligible.some(candidate => candidate.id === item.id)
      })),
      runs: workflowRuns.map(run => ({
        id: run.id,
        name: run.name,
        event: run.event,
        status: run.status,
        conclusion: run.conclusion,
        createdAt: run.created_at,
        updatedAt: run.updated_at,
        url: run.html_url
      }))
    }, {
      headers: { "Cache-Control": "private, no-store, max-age=0" }
    });
  } catch (error) {
    return NextResponse.json(
      { error: error instanceof Error ? error.message : "تعذّر جلب بيانات GitHub." },
      { status: 502, headers: { "Cache-Control": "no-store" } }
    );
  }
}
