import express from "express";
import Database from "better-sqlite3";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const db = new Database("sift.db");
db.pragma("journal_mode = WAL");
db.exec(`CREATE VIRTUAL TABLE IF NOT EXISTS docs USING fts5(path UNINDEXED, name, body);`);

const SKIP = new Set(["node_modules", ".git"]);
const TEXT = new Set([".txt", ".md"]);

function* walk(dir) {
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    if (SKIP.has(e.name)) continue;
    const p = path.join(dir, e.name);
    if (e.isDirectory()) yield* walk(p);
    else if (TEXT.has(path.extname(p).toLowerCase())) yield p;
  }
}

const app = express();
app.use(express.json());

// Enable CORS for Sharon's Vite dev server
app.use((req, res, next) => {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type, X-Sift-Token");
  if (req.method === "OPTIONS") return res.sendStatus(200);
  next();
});

app.get("/health", (_, res) => res.json({ ok: true }));

// Index a folder the user chose
app.post("/index", (req, res) => {
  const folder = req.body?.folder;
  if (!folder || !fs.existsSync(folder)) return res.status(400).json({ error: "Folder not found" });
  const del = db.prepare("DELETE FROM docs WHERE path = ?");
  const ins = db.prepare("INSERT INTO docs(path, name, body) VALUES (?, ?, ?)");

  const indexBatch = db.transaction((folderPath) => {
    let count = 0;
    for (const p of walk(folderPath)) {
      try {
        const text = fs.readFileSync(p, "utf8");
        del.run(p);
        ins.run(p, path.basename(p), text);
        count++;
      } catch (err) {
        // Skip unreadable files
      }
    }
    return count;
  });

  const count = indexBatch(folder);
  res.json({ indexed: count });
});

// Search: GET /search?q=binary trees
app.get("/search", (req, res) => {
  const words = String(req.query.q || "").match(/\w+/g);
  if (!words) return res.json([]);
  const q = words.map((w) => `"${w}"*`).join(" ");
  const rows = db
    .prepare(
      `SELECT path, name, snippet(docs, 2, '[', ']', '…', 12) AS snippet
       FROM docs WHERE docs MATCH ? ORDER BY rank LIMIT 10`
    )
    .all(q);
  res.json(rows);
});

// One-click index deletion
app.delete("/index", (_, res) => {
  db.exec("DELETE FROM docs");
  res.json({ cleared: true });
});

export { app, db };

const isMain = process.argv[1] && fileURLToPath(import.meta.url) === path.resolve(process.argv[1]);
if (isMain) {
  app.listen(4100, "127.0.0.1", () => console.log("Sift agent on http://127.0.0.1:4100"));
}
