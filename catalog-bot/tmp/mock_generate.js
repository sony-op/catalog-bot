require('dotenv').config({ path: require('path').join(__dirname, '../.env') });
const genAI = require('@google/generative-ai');
const fs = require('fs');

const AI = new genAI.GoogleGenerativeAI(process.env.GEMINI_API_KEY);
const getGenerativeModel = () => {
  return AI.getGenerativeModel({
    model: 'gemini-2.5-flash',
    generationConfig: { responseMimeType: "application/json" }
  });
};

async function test() {
  const imageMediaUrl = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==";
  const prompt = `
    You are an AI-powered E-commerce Catalog Generation & Optimization Engine designed to work seamlessly across Web, Android, and iOS applications.
    INPUT:
    - Optional User text: "hello"
    11. OUTPUT FORMAT (IMPORTANT – API & UI FRIENDLY)
    {
      "titles": []
    }
  `;

  try {
    const model = getGenerativeModel();

    let imageParts = [];
    if (imageMediaUrl) {
      if (imageMediaUrl.startsWith('http')) {
        // HTTP logic skipped for mock
      } else {
        let mimeType = 'image/jpeg';
        let base64 = imageMediaUrl;
        if (imageMediaUrl.includes('data:image')) {
          const parts = imageMediaUrl.split(';');
          mimeType = parts[0].split(':')[1];
          base64 = parts[1].split(',')[1];
        }
        imageParts = [{
          inlineData: {
            data: base64,
            mimeType: mimeType
          }
        }];
      }
    }

    const result = await model.generateContent([prompt, ...imageParts]);
    const responseText = result.response.text();
    console.log("SUCCESS");
  } catch (err) {
    fs.writeFileSync('tmp/mock_err.json', JSON.stringify({
      message: err.message,
      name: err.name,
      status: err.status,
      stack: err.stack,
      response: err.response
    }, null, 2));
    console.log("FAIL_WROTE_TO_FILE");
  }
}
test();
