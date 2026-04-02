require('dotenv').config({ path: require('path').join(__dirname, '../.env') });
const genAI = require('@google/generative-ai');

console.log("Using API Key:", process.env.GEMINI_API_KEY ? process.env.GEMINI_API_KEY.substring(0, 10) + '...' : 'UNDEFINED');

const AI = new genAI.GoogleGenerativeAI(process.env.GEMINI_API_KEY);

async function test() {
  try {
    const model = AI.getGenerativeModel({ 
      model: 'gemini-1.5-flash',
      generationConfig: { responseMimeType: "application/json" }
    });
    const result = await model.generateContent("Write a JSON object with a single key 'hello' and value 'world'.");
    console.log("Success:", result.response.text());
  } catch(e) {
    console.error("FAILED MESSAGE:", e.message);
    if(e.response) console.error("FAILED RESPONSE:", JSON.stringify(e.response, null, 2));
  }
}
test();
