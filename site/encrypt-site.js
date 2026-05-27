#!/usr/bin/env node
// Encrypt all .html files in _site/ using AES-256-GCM with a user-supplied passphrase.
// Uses PBKDF2-SHA256 with 100k iterations — compatible with Web Crypto API.
// Usage: node encrypt-site.js <passphrase>

const fs = require("fs");
const path = require("path");
const crypto = require("crypto");

const SITE = path.resolve(__dirname, "../_site");
const ITERATIONS = 100000;
const PATH_PREFIX = process.env.PATH_PREFIX || "/data-for-press-release-2026-05-08/";

if (process.argv.length < 3) {
  console.error("Usage: node encrypt-site.js <passphrase>");
  process.exit(1);
}

const passphrase = process.argv[2];

const salt = crypto.randomBytes(16);
const key = crypto.pbkdf2Sync(passphrase, salt, ITERATIONS, 32, "sha256");

function walk(dir) {
  let files = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) files = files.concat(walk(full));
    else if (entry.isFile() && entry.name.endsWith(".html")) files.push(full);
  }
  return files;
}

const htmlFiles = walk(SITE);
console.log(`Encrypting ${htmlFiles.length} HTML files...`);

const saltB64 = salt.toString("base64");

for (const fpath of htmlFiles) {
  const plaintext = fs.readFileSync(fpath, "utf8");

  const iv = crypto.randomBytes(12);
  const cipher = crypto.createCipheriv("aes-256-gcm", key, iv);
  const encrypted = Buffer.concat([
    cipher.update(plaintext, "utf8"),
    cipher.final(),
  ]);
  const tag = cipher.getAuthTag();

  // Pack: iv(12) + tag(16) + ciphertext
  const payload = Buffer.concat([iv, tag, encrypted]);
  const b64 = payload.toString("base64");

  const stub = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="encrypted" content="true">
  <title>No Flock for SoPo</title>
  <link rel="stylesheet" href="${PATH_PREFIX}assets/style.css">
  <link rel="stylesheet" href="${PATH_PREFIX}gate.css">
  <script>
  (function(){
    var t=localStorage.getItem('theme');
    if(t)document.documentElement.setAttribute('data-theme',t);
    else if(window.matchMedia('(prefers-color-scheme:dark)').matches)document.documentElement.setAttribute('data-theme','dark');
  })();
  </script>
  <script>window._enc="${b64}";</script>
</head>
<body>
  <nav>
    <a href="${PATH_PREFIX}" class="nav-home">No Flock for SoPo</a>
    <button class="theme-toggle" onclick="(function(){var d=document.documentElement,n=d.getAttribute('data-theme'),v=n==='dark'?'light':'dark';d.setAttribute('data-theme',v);localStorage.setItem('theme',v);})()">&#9681;</button>
  </nav>
  <main>
    <div id="gate-box">
      <h1>Access Required</h1>
      <p>Enter the code provided by No Flock for SoPo to view this site.</p>
      <form id="gate-form">
        <input type="password" id="gate-input" placeholder="Access code" autofocus>
        <button type="submit" id="gate-submit">Enter</button>
      </form>
      <p id="gate-error"></p>
    </div>
  </main>
  <footer>
    <p>Data from FOAA-obtained Flock Safety audit logs, South Portland Police Department.</p>
  </footer>
  <script src="${PATH_PREFIX}gate.js" data-salt="${saltB64}" data-iterations="${ITERATIONS}"></script>
</body>
</html>`;

  fs.writeFileSync(fpath, stub);
}

const gateJs = fs.readFileSync(path.join(__dirname, "gate.js"), "utf8");
fs.writeFileSync(path.join(SITE, "gate.js"), gateJs);

const gateCss = fs.readFileSync(path.join(__dirname, "gate.css"), "utf8");
fs.writeFileSync(path.join(SITE, "gate.css"), gateCss);

console.log("Done. Encrypted " + htmlFiles.length + " files. gate.js + gate.css written.");
console.log("Salt (base64): " + saltB64);