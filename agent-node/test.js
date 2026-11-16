import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { app, db } from "./index.js";

// Helper to run express requests without network port in unit tests
async function request(method, url, body = null) {
  return new Promise((resolve, reject) => {
    const server = app.listen(0, "127.0.0.1", async () => {
      const port = server.address().port;
      try {
        const options = {
          method,
          headers: body ? { "Content-Type": "application/json" } : {},
        };
        if (body) {
          options.body = JSON.stringify(body);
        }
        const res = await fetch(`http://127.0.0.1:${port}${url}`, options);
        const json = await res.json();
        server.close();
        resolve({ status: res.status, json });
      } catch (err) {
        server.close();
        reject(err);
      }
    });
  });
}

test("GET /health returns ok", async () => {
  const res = await request("GET", "/health");
  assert.equal(res.status, 200);
  assert.deepEqual(res.json, { ok: true });
});

test("POST /index with invalid folder returns 400", async () => {
  const res = await request("POST", "/index", { folder: "C:/non_existent_folder_abc_123" });
  assert.equal(res.status, 400);
  assert.equal(res.json.error, "Folder not found");
});

test("Full indexing, search, and delete lifecycle", async () => {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "sift-test-"));
  const notePath = path.join(tmpDir, "binary_tree.txt");
  fs.writeFileSync(
    notePath,
    "A binary search tree and binary trees are fundamental data structures with key invariant properties."
  );

  // 1. Index folder
  const resIndex = await request("POST", "/index", { folder: tmpDir });
  assert.equal(resIndex.status, 200);
  assert.ok(resIndex.json.indexed >= 1);

  // 2. Search
  const resSearch = await request("GET", "/search?q=binary%20trees");
  assert.equal(resSearch.status, 200);
  assert.ok(resSearch.json.length >= 1);
  assert.equal(resSearch.json[0].name, "binary_tree.txt");
  assert.match(resSearch.json[0].snippet, /binary/i);

  // 3. Special characters in search query should not throw
  const resPunct = await request("GET", "/search?q=AND%20OR%20NOT%20*%20()%20\"");
  assert.equal(resPunct.status, 200);

  // 4. Delete index
  const resDelete = await request("DELETE", "/index");
  assert.equal(resDelete.status, 200);
  assert.deepEqual(resDelete.json, { cleared: true });

  // 5. Search after delete
  const resEmpty = await request("GET", "/search?q=binary");
  assert.equal(resEmpty.status, 200);
  assert.equal(resEmpty.json.length, 0);

  // Clean up temp folder
  fs.rmSync(tmpDir, { recursive: true, force: true });
});
