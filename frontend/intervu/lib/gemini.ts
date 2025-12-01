import OpenAI from "openai";

const apiKey = process.env.OPENAI_API_KEY;
const modelName = process.env.OPENAI_MODEL || "gpt-4o-mini";

if (!apiKey) {
  console.warn("⚠️ OPENAI_API_KEY is not set in frontend/.env");
}

const openai = apiKey ? new OpenAI({ apiKey }) : null;

interface QuestionParams {
  role: string;
  level: string;
  type: string;      // technical / behavioural / mixed
  techstack: string;
  amount: number;
  userid?: string;
}

export async function generateInterviewQuestions(params: QuestionParams) {
  if (!openai) {
    throw new Error("Missing OPENAI_API_KEY – OpenAI client not initialized");
  }

  const { role, level, type, techstack, amount, userid } = params;

  const systemPrompt = `
You are an expert technical interviewer.

Generate exactly ${amount} interview questions for this candidate:
- Role: ${role}
- Level: ${level}
- Interview type: ${type} (technical / behavioural / mixed)
- Tech stack: ${techstack || "not specified"}
- User id (for context only): ${userid || "N/A"}

Return the questions as a simple bullet list, one question per line, for example:

- Question 1 ...
- Question 2 ...
- Question 3 ...

Do NOT include explanations or any text before/after the list.
  `.trim();

  const completion = await openai.chat.completions.create({
    model: modelName,
    temperature: 0.7,
    messages: [{ role: "system", content: systemPrompt }],
  });

  const content = completion.choices[0]?.message?.content ?? "";
  const lines = content.split("\n").map((l) => l.trim()).filter(Boolean);

  // strip bullets / numbering
  const questions = lines
    .map((line) => line.replace(/^[-*•\d\.\)]\s*/, "").trim())
    .filter((line) => line.length > 0);

  if (questions.length === 0) {
    console.error("❌ OpenAI returned no questions. Raw content:", content);
    throw new Error("OpenAI did not return any questions");
  }

  // return array of strings, same shape as before
  return questions;
}
