// ESLint v9 flat config for VaayuTrade
import js from '@eslint/js';
import eslintConfigPrettier from 'eslint-config-prettier';
import importPlugin from 'eslint-plugin-import';
import nPlugin from 'eslint-plugin-n';
import promisePlugin from 'eslint-plugin-promise';
import tseslint from 'typescript-eslint';

export default [
  // Ignore patterns (flat-config style)
  {
    ignores: [
      'node_modules/',
      'dist/',
      'build/',
      '.next/',
      'coverage/',
      '**/*.d.ts',
      'commitlint.config.cjs'
    ],
  },

  // Base JS rules
  js.configs.recommended,

  // TypeScript recommended rules (parser + plugin)
  ...tseslint.configs.recommended,

  // Plugins (import, n, promise)
  {
    plugins: {
      import: importPlugin,
      n: nPlugin,
      promise: promisePlugin,
    },
    rules: {
      // Keep import order rule from previous config
      'import/order': ['warn', { 'newlines-between': 'always', alphabetize: { order: 'asc' } }],
    },
    languageOptions: {
      parser: tseslint.parser,
      parserOptions: {
        ecmaVersion: 'latest',
        sourceType: 'module',
        // project: false to avoid requiring a tsconfig for every package at this stage
      },
    },
  },

  // Disable stylistic conflicts; Prettier is the formatter
  eslintConfigPrettier,
];
