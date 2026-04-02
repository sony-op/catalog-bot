require('dotenv').config({ path: require('path').join(__dirname, '../.env') });
const gemini = require('../src/services/gemini');
const fs = require('fs');

async function test() {
  const pixel = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==";
  try {
    const res = await gemini.generateCatalogData(pixel, "hello");
    console.log("SUCCESS:", res);
  } catch (err) {
    console.error("FAILED. WROTE ERRDUMP.");
    fs.writeFileSync('err_dump.json', JSON.stringify({
      message: err.message, stack: err.stack
    }, null, 2));
  }
}
test();
