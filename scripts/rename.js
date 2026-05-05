#!/usr/bin/env node
/**
 * Rename the project. Usage: pnpm rename <new-name>
 *
 * Replaces "bakebook" with the new name in:
 * - All package.json files
 * - README.md
 * - docker-compose.yml
 * - Coolify service names (noted in comments where relevant)
 */

const fs = require("fs");
const path = require("path");

const newName = process.argv[2];
if (!newName) {
  console.error("Usage: pnpm rename <new-name>");
  process.exit(1);
}

const oldName = "bakebook";
const filesToUpdate = [
  "package.json",
  "apps/web/package.json",
  "apps/api/pyproject.toml",
  "packages/types/package.json",
  "docker-compose.yml",
  "README.md",
];

for (const file of filesToUpdate) {
  const fullPath = path.resolve(__dirname, "..", file);
  if (fs.existsSync(fullPath)) {
    let content = fs.readFileSync(fullPath, "utf8");
    content = content.replaceAll(oldName, newName);
    fs.writeFileSync(fullPath, content);
    console.log(`Updated: ${file}`);
  }
}

console.log(`\nRenamed to "${newName}". Also update Coolify service names manually.`);
