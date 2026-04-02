require('dotenv').config({ path: require('path').join(__dirname, '../.env') });
const genAI = require('@google/generative-ai');
const fs = require('fs');

const AI = new genAI.GoogleGenerativeAI(process.env.GEMINI_API_KEY);

async function test() {
  try {
    const model = AI.getGenerativeModel({ 
      model: 'gemini-1.5-flash-latest',
      generationConfig: { responseMimeType: "application/json" }
    });
    const result = await model.generateContent("hello");
    console.log("SUCCESS");
  } catch(e) {
    fs.writeFileSync('tmp/err_real.json', JSON.stringify({
      message: e.message,
      status: e.status,
      details: e.details
    }, null, 2));
    console.log("FAILED_WROTE_TO_FILE");
  }
}
test();
