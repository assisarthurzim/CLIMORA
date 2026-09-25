// Verifies every named import between project modules resolves to a real
// export. A renamed export otherwise fails only when the component renders.
const fs = require('fs');
const path = require('path');

function walk(dir) {
  return fs
    .readdirSync(dir, { withFileTypes: true })
    .flatMap((entry) =>
      entry.isDirectory() ? walk(path.join(dir, entry.name)) : [path.join(dir, entry.name)],
    );
}

const files = walk('src').filter((file) => /\.(js|jsx)$/.test(file));
const exported = new Map();

for (const file of files) {
  const source = fs.readFileSync(file, 'utf8');
  const names = [
    ...source.matchAll(/export\s+(?:async\s+)?(?:function|const|class)\s+(\w+)/g),
  ].map((match) => match[1]);
  if (/export\s+default/.test(source)) names.push('default');

  const key = file.replace(/\\/g, '/').replace(/^src\//, '').replace(/\.(js|jsx)$/, '');
  exported.set(key, names);
}

let problems = 0;

for (const file of files) {
  const source = fs.readFileSync(file, 'utf8');
  for (const match of source.matchAll(/import\s+\{([^}]+)\}\s+from\s+'@\/([^']+)'/g)) {
    const base = match[2].replace(/\.(js|jsx)$/, '');
    // A bare directory import resolves to its index file.
    const available = exported.get(base) ?? exported.get(`${base}/index`);

    if (!available) {
      console.log(`MODULO AUSENTE ${file} -> ${match[2]}`);
      problems += 1;
      continue;
    }

    for (const raw of match[1].split(',')) {
      const name = raw.trim().split(/\s+as\s+/)[0];
      if (name && !available.includes(name)) {
        console.log(`NOME AUSENTE ${file} -> '${name}' nao existe em ${match[2]}`);
        problems += 1;
      }
    }
  }
}

if (problems > 0) {
  console.log(`Problemas encontrados: ${problems}`);
  process.exit(1);
}
console.log(`Imports do frontend OK em ${files.length} arquivos.`);
