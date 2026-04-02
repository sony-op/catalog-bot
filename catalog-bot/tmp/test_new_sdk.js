require('dotenv').config({ path: require('path').join(__dirname, '../.env') });
const { GoogleGenAI } = require('@google/genai');

async function test() {
  const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });
  const pixel = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==";
  
  const mimeType = 'image/png';
  const data = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==';

  try {
    const response = await ai.models.generateContent({
      model: 'gemini-2.5-flash',
      contents: [
        'hello',
        {
          inlineData: { data, mimeType }
        }
      ],
      config: {
        responseMimeType: "application/json",
      }
    });
    console.log("SUCCESS:", response.text);
  } catch (err) {
    console.error("FAIL:", err.message);
  }
}
test();
