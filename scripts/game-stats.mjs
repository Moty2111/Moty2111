#!/usr/bin/env node
/**
 * Generates assets/game-stats.svg — a single dashboard with three panels:
 * RACE (yearly commit progress), CHARACTER (attributes from real activity)
 * and TERMINAL (repo/community numbers).
 *
 * Data: GitHub REST + GraphQL. Set GITHUB_TOKEN for higher rate limits
 * and the contribution calendar. Runs in GitHub Actions, no dependencies.
 */
import { writeFileSync, mkdirSync } from "node:fs";

const LOGIN = process.env.GH_LOGIN || "Moty2111";
const TOKEN = process.env.GITHUB_TOKEN || "";
const GOAL = Number(process.env.RACE_GOAL || 500);
const OUT = "assets/game-stats.svg";

const API = "https://api.github.com";
const headers = {
  Accept: "application/vnd.github+json",
  "User-Agent": `${LOGIN}-profile-stats`,
  ...(TOKEN ? { Authorization: `Bearer ${TOKEN}` } : {}),
};

const clamp = (n, min, max) => Math.max(min, Math.min(max, n));
const esc = (s) =>
  String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const num = (n) => Number(n || 0).toLocaleString("en-US");

async function getJson(url, options = {}) {
  const res = await fetch(url, { headers, ...options });
  if (!res.ok) throw new Error(`${res.status} ${res.statusText} — ${url}`);
  return res.json();
}

async function loadData() {
  const [user, repos] = await Promise.all([
    getJson(`${API}/users/${LOGIN}`),
    getJson(`${API}/users/${LOGIN}/repos?per_page=100&sort=updated`),
  ]);

  const ownRepos = repos.filter((r) => !r.fork);
  const stars = ownRepos.reduce((sum, r) => sum + (r.stargazers_count || 0), 0);
  const languages = new Set(ownRepos.map((r) => r.language).filter(Boolean));

  let commitsYear = 0;
  let streak = 0;
  let bestDay = 0;
  let activeDays = 0;
  let lastActive = null;

  if (TOKEN) {
    try {
      const q = `query($login: String!) {
        user(login: $login) {
          contributionsCollection {
            totalCommitContributions
            contributionCalendar {
              totalContributions
              weeks { contributionDays { date contributionCount } }
            }
          }
          repositories(first: 100, ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC) {
            nodes { stargazerCount }
          }
        }
      }`;
      const res = await fetch("https://api.github.com/graphql", {
        method: "POST",
        headers: { ...headers, "Content-Type": "application/json" },
        body: JSON.stringify({ query: q, variables: { login: LOGIN } }),
      });
      if (res.ok) {
        const json = await res.json();
        const u = json?.data?.user;
        const cal = u?.contributionsCollection?.contributionCalendar;
        commitsYear = u?.contributionsCollection?.totalCommitContributions ?? 0;
        if (cal?.weeks) {
          const days = cal.weeks.flatMap((w) => w.contributionDays);
          days.sort((a, b) => a.date.localeCompare(b.date));
          bestDay = days.reduce((m, d) => Math.max(m, d.contributionCount), 0);
          activeDays = days.filter((d) => d.contributionCount > 0).length;
          const last = [...days].reverse().find((d) => d.contributionCount > 0);
          lastActive = last ? last.date : null;
          for (let i = days.length - 1; i >= 0; i -= 1) {
            if (days[i].contributionCount > 0) streak += 1;
            else break;
          }
        }
      }
    } catch (err) {
      console.warn(`GraphQL unavailable: ${err.message}`);
    }
  }

  if (!commitsYear) {
    // Fallback without a token: count commit-ish events from the public feed.
    try {
      const events = await getJson(`${API}/users/${LOGIN}/events/public?per_page=100`);
      commitsYear = events
        .filter((e) => e.type === "PushEvent")
        .reduce((sum, e) => sum + (e.payload?.commits?.length || 1), 0);
    } catch {
      commitsYear = 0;
    }
  }

  if (!lastActive) {
    try {
      const events = await getJson(`${API}/users/${LOGIN}/events/public?per_page=1`);
      lastActive = events[0]?.created_at?.slice(0, 10) || null;
    } catch {
      /* ignore */
    }
  }

  return {
    repos: user.public_repos ?? ownRepos.length,
    followers: user.followers ?? 0,
    stars,
    languages: languages.size,
    commitsYear,
    streak,
    bestDay,
    activeDays,
    lastActive,
    since: (user.created_at || "").slice(0, 4),
  };
}

function relativeDay(iso) {
  if (!iso) return "no data";
  const then = new Date(`${iso}T00:00:00Z`).getTime();
  const days = Math.max(0, Math.round((Date.now() - then) / 86400000));
  if (days === 0) return "today";
  if (days === 1) return "yesterday";
  if (days < 30) return `${days} days ago`;
  return `${Math.round(days / 30)} mo ago`;
}

function svg(data) {
  const { repos, followers, stars, languages, commitsYear, streak, bestDay, lastActive, since } = data;

  const pct = clamp(Math.round((commitsYear / GOAL) * 100), 3, 100);
  const level = clamp(1 + Math.floor(Math.sqrt(commitsYear) / 2), 1, 99);
  const xp = commitsYear % 50;
  const attrs = [
    { key: "STR", value: clamp(Math.round(Math.sqrt(commitsYear) * 4.6), 4, 99) },
    { key: "AGI", value: clamp(streak * 5 + 6, 4, 99) },
    { key: "INT", value: clamp(languages * 13 + 8, 4, 99) },
    { key: "CHA", value: clamp(followers * 9 + stars * 3 + 8, 4, 99) },
  ];

  const W = 900;
  const H = 330;
  const pad = 24;
  const gap = 14;
  const panelW = (W - pad * 2 - gap * 2) / 3; // 274.67
  const panelH = 224;
  const top = 60;

  const panel = (x, title, accent) => `
    <g>
      <rect x="${x}" y="${top}" width="${panelW}" height="${panelH}" rx="16"
            fill="#0b0e16" stroke="#ffffff" stroke-opacity="0.07" />
      <rect x="${x}" y="${top}" width="${panelW}" height="1" fill="${accent}" opacity="0.55" />
      <text x="${x + 18}" y="${top + 26}" fill="#7e879b" font-size="10.5"
            font-family="ui-monospace, 'SF Mono', Consolas, monospace" letter-spacing="2.2">${title}</text>
    </g>`;

  const barX = (x) => x + 18;
  const barW = panelW - 36;

  return `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}" role="img"
     aria-label="Game stats: ${commitsYear} commits this year, level ${level}, ${repos} repositories">
  <defs>
    <linearGradient id="accent" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#b69bff" />
      <stop offset="0.5" stop-color="#6fe7f5" />
      <stop offset="1" stop-color="#ffa4cf" />
    </linearGradient>
    <linearGradient id="track" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#7c5cff" />
      <stop offset="0.55" stop-color="#33d6ea" />
      <stop offset="1" stop-color="#ff7fbf" />
    </linearGradient>
    <radialGradient id="glowA" cx="0.12" cy="0" r="0.9">
      <stop offset="0" stop-color="#7c5cff" stop-opacity="0.35" />
      <stop offset="1" stop-color="#7c5cff" stop-opacity="0" />
    </radialGradient>
    <radialGradient id="glowB" cx="0.95" cy="1" r="0.8">
      <stop offset="0" stop-color="#1ed2eb" stop-opacity="0.22" />
      <stop offset="1" stop-color="#1ed2eb" stop-opacity="0" />
    </radialGradient>
    <clipPath id="frame"><rect x="0" y="0" width="${W}" height="${H}" rx="20" /></clipPath>
  </defs>

  <g clip-path="url(#frame)">
    <rect width="${W}" height="${H}" fill="#06070b" />
    <rect width="${W}" height="${H}" fill="url(#glowA)" />
    <rect width="${W}" height="${H}" fill="url(#glowB)" />
    <g stroke="#ffffff" stroke-opacity="0.028">
      ${Array.from({ length: 18 }, (_, i) => `<path d="M${i * 56} 0V${H}" />`).join("")}
      ${Array.from({ length: 7 }, (_, i) => `<path d="M0 ${i * 56}H${W}" />`).join("")}
    </g>
  </g>
  <rect x="0.5" y="0.5" width="${W - 1}" height="${H - 1}" rx="19.5" fill="none"
        stroke="#ffffff" stroke-opacity="0.09" />

  <text x="${pad}" y="32" fill="#eef0f7" font-size="13" font-weight="600" letter-spacing="3.4"
        font-family="ui-monospace, 'SF Mono', Consolas, monospace">GAME STATS</text>
  <text x="${W - pad}" y="32" text-anchor="end" fill="#6f7789" font-size="10.5"
        font-family="ui-monospace, 'SF Mono', Consolas, monospace">@${LOGIN} · live since ${since}</text>

  ${panel(pad, "RACE", "#6fe7f5")}
  <text x="${pad + 18}" y="${top + 76}" fill="url(#accent)" font-size="38" font-weight="700"
        font-family="'Segoe UI', system-ui, sans-serif">${pct}%</text>
  <text x="${pad + 18}" y="${top + 98}" fill="#7e879b" font-size="11"
        font-family="'Segoe UI', system-ui, sans-serif">${num(commitsYear)} of ${num(GOAL)} commits in the last year</text>

  <rect x="${barX(pad)}" y="${top + 126}" width="${barW}" height="8" rx="4" fill="#171c29" />
  <rect x="${barX(pad)}" y="${top + 126}" width="${(barW * pct) / 100}" height="8" rx="4" fill="url(#track)" />
  <g transform="translate(${barX(pad) + (barW * pct) / 100}, ${top + 130})">
    <path d="M-13 -5 L-2 -5 L3 0 L-2 5 L-13 5 Z" fill="#eef0f7" />
    <circle cx="-8" cy="6" r="2.6" fill="#06070b" stroke="#eef0f7" stroke-width="1.4" />
    <circle cx="0" cy="6" r="2.6" fill="#06070b" stroke="#eef0f7" stroke-width="1.4" />
  </g>
  <g fill="#6f7789" font-size="10.5" font-family="'Segoe UI', system-ui, sans-serif">
    <text x="${barX(pad)}" y="${top + 158}">Streak</text>
    <text x="${barX(pad) + 96}" y="${top + 158}">Best day</text>
    <text x="${barX(pad) + 186}" y="${top + 158}">Active</text>
  </g>
  <g fill="#d8dce8" font-size="15" font-weight="600" font-family="'Segoe UI', system-ui, sans-serif">
    <text x="${barX(pad)}" y="${top + 180}">${streak}<tspan font-size="10" font-weight="400" fill="#6f7789"> d</tspan></text>
    <text x="${barX(pad) + 96}" y="${top + 180}">${bestDay}<tspan font-size="10" font-weight="400" fill="#6f7789"> c</tspan></text>
    <text x="${barX(pad) + 186}" y="${top + 180}">${data.activeDays}<tspan font-size="10" font-weight="400" fill="#6f7789"> d</tspan></text>
  </g>
  <text x="${barX(pad)}" y="${top + 204}" fill="#5b6276" font-size="9.5"
        font-family="'Segoe UI', system-ui, sans-serif">Updated by GitHub Actions every day</text>

  ${panel(pad + panelW + gap, "CHARACTER", "#b69bff")}
  <text x="${pad + panelW + gap + 18}" y="${top + 58}" fill="#7e879b" font-size="10"
        font-family="'Segoe UI', system-ui, sans-serif">LEVEL</text>
  <text x="${pad + panelW + gap + 18}" y="${top + 96}" fill="#eef0f7" font-size="30" font-weight="700"
        font-family="'Segoe UI', system-ui, sans-serif">${level}</text>
  <rect x="${pad + panelW + gap + 62}" y="${top + 70}" width="76" height="20" rx="10"
        fill="#171c29" stroke="#b69bff" stroke-opacity="0.45" />
  <text x="${pad + panelW + gap + 100}" y="${top + 84}" text-anchor="middle" fill="#b69bff" font-size="9.5"
        font-family="ui-monospace, 'SF Mono', Consolas, monospace" letter-spacing="1">FULLSTACK</text>

  ${attrs
    .map((a, i) => {
      const y = top + 118 + i * 22;
      const w = (94 * a.value) / 99;
      const x = pad + panelW + gap + 56;
      return `
  <text x="${pad + panelW + gap + 18}" y="${y + 4}" fill="#8b93a7" font-size="9.5" letter-spacing="1"
        font-family="ui-monospace, 'SF Mono', Consolas, monospace">${a.key}</text>
  <rect x="${x}" y="${y - 4}" width="94" height="6" rx="3" fill="#171c29" />
  <rect x="${x}" y="${y - 4}" width="${w}" height="6" rx="3" fill="url(#accent)" opacity="0.9" />
  <text x="${x + 118}" y="${y + 3}" fill="#c7ccda" font-size="10"
        font-family="ui-monospace, 'SF Mono', Consolas, monospace">${a.value}</text>`;
    })
    .join("")}

  <text x="${pad + panelW + gap + 18}" y="${top + 208}" fill="#5b6276" font-size="9.5"
        font-family="'Segoe UI', system-ui, sans-serif">XP ${xp} / 50 · next level ${level + 1}</text>

  ${panel(pad + (panelW + gap) * 2, "TERMINAL", "#4ade80")}
  <g font-family="ui-monospace, 'SF Mono', Consolas, monospace" font-size="11">
    <text x="${pad + (panelW + gap) * 2 + 18}" y="${top + 62}" fill="#4ade80">$ gh stats --user</text>
    <text x="${pad + (panelW + gap) * 2 + 18}" y="${top + 88}" fill="#8b93a7">repos<tspan fill="#eef0f7">      ${num(repos)}</tspan></text>
    <text x="${pad + (panelW + gap) * 2 + 18}" y="${top + 108}" fill="#8b93a7">stars<tspan fill="#eef0f7">      ${num(stars)}</tspan></text>
    <text x="${pad + (panelW + gap) * 2 + 18}" y="${top + 128}" fill="#8b93a7">followers<tspan fill="#eef0f7">  ${num(followers)}</tspan></text>
    <text x="${pad + (panelW + gap) * 2 + 18}" y="${top + 148}" fill="#8b93a7">languages<tspan fill="#eef0f7">  ${num(languages)}</tspan></text>
    <text x="${pad + (panelW + gap) * 2 + 18}" y="${top + 172}" fill="#8b93a7">last push<tspan fill="#eef0f7">  ${relativeDay(lastActive)}</tspan></text>
    <text x="${pad + (panelW + gap) * 2 + 18}" y="${top + 198}" fill="#4ade80">&gt; status: online</text>
    <rect x="${pad + (panelW + gap) * 2 + 146}" y="${top + 188}" width="7" height="11" fill="#4ade80">
      <animate attributeName="opacity" values="1;1;0;0" dur="1.4s" repeatCount="indefinite" />
    </rect>
  </g>
</svg>
`;
}

const data = await loadData();
mkdirSync("assets", { recursive: true });
writeFileSync(OUT, svg(data));
console.log(
  `game-stats.svg: ${data.commitsYear} commits, streak ${data.streak}, ` +
    `${data.repos} repos, ${data.stars} stars, ${data.followers} followers, ${data.languages} languages`,
);
