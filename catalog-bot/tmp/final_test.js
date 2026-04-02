require('dotenv').config({ path: require('path').join(__dirname, '../.env') });
const genAI = require('@google/generative-ai');
const AI = new genAI.GoogleGenerativeAI(process.env.GEMINI_API_KEY);

async function run() {
  const pixel = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==";
  const parts = pixel.split(';');
  const mimeType = parts[0].split(':')[1];
  const base64 = parts[1].split(',')[1];
  
  const imageParts = [{
    inlineData: {
      data: base64,
      mimeType: mimeType
    }
  }];
  
  try {
    const model = AI.getGenerativeModel({ 
      model: 'gemini-2.5-flash',
      generationConfig: { responseMimeType: "application/json" }
    });
    console.log("SENDING REQUEST WITH IMAGE...");
    const result = await model.generateContent(["hello. output format: { \"msg\": \"hello\" }", ...imageParts]);
    console.log("SUCCESS:", result.response.text());
  } catch (err) {
    console.error("FAIL:", err.message);
  }
}
run();
