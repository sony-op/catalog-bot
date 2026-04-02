require('dotenv').config({ path: require('path').join(__dirname, '../.env') });
async function run() {
  try {
    const res = await fetch(`https://generativelanguage.googleapis.com/v1beta/models?key=${process.env.GEMINI_API_KEY}`);
    const data = await res.json();
    require('fs').writeFileSync('tmp/models.json', JSON.stringify(data, null, 2));
  } catch (e) {
    require('fs').writeFileSync('tmp/models.json', JSON.stringify({ error: e.message }));
  }
}
run();
