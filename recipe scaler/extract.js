const { execSync } = require('child_process');
const log = execSync('git log -S "ingredientMap" -p', { encoding: 'utf8', maxBuffer: 10 * 1024 * 1024 });
const fs = require('fs');
fs.writeFileSync('extracted_log.txt', log);
