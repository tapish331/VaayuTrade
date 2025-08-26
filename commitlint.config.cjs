/** @type {import('@commitlint/types').UserConfig} */
module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'subject-case': [2, 'always', ['sentence-case', 'start-case', 'pascal-case', 'lower-case']],
    'scope-enum': [2, 'always', [
      'repo','docs','license','api','dashboard','traderd','infra','strategy','backtester','broker-kite','common'
    ]]
  }
};
