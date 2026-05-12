const fs = require('fs');
const content = fs.readFileSync('ui-controller.js', 'utf-8');

// Mock DOM & global
global.window = {};
global.document = {
  getElementById: (id) => ({ value: 'malayalam' }),
  createElement: () => ({ style: {} }),
  querySelectorAll: () => ([]),
  addEventListener: () => {}
};
global.alert = () => {};
global.getElement = (id) => ({ value: 'malayalam' });


// Evaluate all code inside a closure so we don't pollute global directly, but actually it's easier to just eval
try {
  eval(content);
  
  // Now test processTranslation
  const tests = [
    { text: "tomato", expected: "തക്കാളി" },
    { text: "green chilli", expected: "പച്ചമുളക്" },
    { text: "1 cup sugar", expected: "1 കപ്പ് പഞ്ചസാര" }
  ];
  
  let passed = 0;
  tests.forEach(t => {
    let out = processTranslation(t.text, "malayalam");
    if (out === t.expected || out.includes(t.expected)) passed++;
  });
  
  console.log("UNIT TESTS PASSED: " + passed + "/" + tests.length);
  process.exit(0);
} catch (err) {
  console.error(err);
  process.exit(1);
}
