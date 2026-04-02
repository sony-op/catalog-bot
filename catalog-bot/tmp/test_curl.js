require('dotenv').config({ path: require('path').join(__dirname, '../.env') });
const axios = require('axios');

async function test() {
  const pixel = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==";
  const url = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${process.env.GEMINI_API_KEY}`;
  
  try {
    const res = await axios.post(url, {
      contents: [
        {
          parts: [
            { text: "hello" },
            { inlineData: { mimeType: "image/png", data: pixel } }
          ]
        }
      ]
    }, { headers: { 'x-goog-api-key': process.env.GEMINI_API_KEY } });
    console.log("SUCCESS:", JSON.stringify(res.data));
  } catch (err) {
    console.error("FAIL:", err.response ? JSON.stringify(err.response.data) : err.message);
  }
}
test();
