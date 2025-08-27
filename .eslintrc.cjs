/* eslint-env node */
module.exports = {
  root: true,
  env: { es2023: true, node: true, browser: false },
  parser: "@typescript-eslint/parser",
  parserOptions: { ecmaVersion: "latest", sourceType: "module", project: false },
  plugins: ["@typescript-eslint", "import", "promise", "n"],
  extends: [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:import/recommended",
    "plugin:n/recommended",
    "plugin:promise/recommended",
    "prettier"
  ],
  ignorePatterns: ["node_modules/", "dist/", "build/", ".next/", "**/*.d.ts"],
  rules: {
    "import/order": ["warn", { "newlines-between": "always", "alphabetize": { "order": "asc" } }]
  }
};
