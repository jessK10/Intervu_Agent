import OpenAI from "openai";

if (!process.env.OPENAI_API_KEY) {
  throw new Error("❌ Missing OPENAI_API_KEY in .env.local");
}

const client = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

interface QuestionParams {
  role: string;
  level: string;
  type: string;
  techstack: string;
  amount: number;
  userid?: string;
}

export async function generateInterviewQuestions(params: QuestionParams) {
  const prompt = `
  Generate ${params.amount} interview questions in JSON format.

  Role: ${params.role}
  Level: ${params.level}
  Interview type: ${params.type} (technical / behavioural / mixed)
  Tech stack: ${params.techstack}
  UserId: ${params.userid || "N/A"}

  Return ONLY valid JSON like this:
  {
    "questions": [
      "Question 1",
      "Question 2"
    ]
  }
  `;

  try {
    const response = await client.chat.completions.create({
      model: "gpt-4o-mini", // ✅ good for Q&A, low cost
      messages: [{ role: "user", content: prompt }],
    });

    const text = response.choices[0].message?.content || "";

    // clean any ```json wrapper
    const cleaned = text.replace(/```json|```/g, "").trim();

    const parsed = JSON.parse(cleaned);
    return parsed.questions || [];
  } catch (err) {
    console.error("❌ OpenAI error:", err);
    throw new Error("Failed to generate interview questions");
  }
}
