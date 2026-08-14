import { GoogleGenAI } from "@google/genai";
import { NextRequest, NextResponse } from "next/server";

const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY || "" });

export async function POST(req: NextRequest) {
  try {
    const { action, payload } = await req.json();

    if (!process.env.GEMINI_API_KEY) {
      return NextResponse.json(
        { error: "GEMINI_API_KEY is not configured in the environment." },
        { status: 500 }
      );
    }

    if (action === "intake_chat") {
      // payload has { messages: Array<{role: string, content: string}> }
      const messages = payload.messages || [];
      const chatHistory = messages.map((m: any) => ({
        role: m.role === "assistant" ? "model" : "user",
        parts: [{ text: m.content }]
      }));

      const systemInstruction = `You are the expert Intake Agent for the AI Negotiation Platform.
Your task is to interview the user to build a structured requirement for their service needs (e.g., movers, plumbers, roofers, painters).
You must extract:
1. The service type (e.g., residential moving, water pipe leak repair, roof replacement).
2. The location (city and state/zip).
3. The specific details/scope (e.g., 2 bedroom apartment, brand or material preferences, timeframe).

Be warm, polite, and professional. Ask one clear question at a time to keep the interaction simple.
At the end of every message, evaluate if we have enough info (at least service type and location) and output a JSON block at the very bottom in this exact format so our parsing engine can read it:
---
{
  "service_type": "string or null",
  "location": "string or null",
  "details": {},
  "is_complete": true/false,
  "follow_up_question": "next question or null"
}
---`;

      const response = await ai.models.generateContent({
        model: "gemini-2.5-flash",
        contents: chatHistory,
        config: {
          systemInstruction,
          temperature: 0.7,
        }
      });

      return NextResponse.json({ text: response.text });
    }

    if (action === "generate_call_plan") {
      // payload has { service_type, location, details, candidates }
      const { service_type, location, details, candidates } = payload;
      const prompt = `Analyze this service requirement and the discovered candidate vendors:
Requirement: Service: ${service_type}, Location: ${location}, Details: ${JSON.stringify(details)}
Vendors: ${JSON.stringify(candidates)}

Generate an expert Negotiation Call Plan in JSON format:
{
  "strategy": "Describe a detailed negotiation strategy (e.g. Ask for first-time customer discount, negotiate based on competitive matching)",
  "max_calls": 3,
  "focus_areas": [
    "Verify availability for the target dates",
    "Request flat-rate quote instead of hourly rate",
    "Inquire about standard insurance coverage"
  ]
}`;

      const response = await ai.models.generateContent({
        model: "gemini-2.5-flash",
        contents: prompt,
        config: {
          responseMimeType: "application/json",
          temperature: 0.2,
        }
      });

      return NextResponse.json(JSON.parse(response.text || "{}"));
    }

    if (action === "simulate_call") {
      // payload has { business, call_plan, requirement }
      const { business, call_plan, requirement } = payload;
      const prompt = `Simulate an outbound voice call from our AI Negotiation Agent to the business: "${business.name}" (Phone: ${business.phone}).
The service requirement is: ${JSON.stringify(requirement)}
The negotiation strategy we are using is: ${call_plan.strategy}

Generate a realistic, professional, multi-turn phone call transcript between the AI Agent ("AI Agent") and the business representative ("Vendor").
Show the negotiation happening - the agent should politely ask for availability, describe the job, ask for their standard pricing, apply the strategy (e.g., asking for discounts, quoting competitors' ranges, or finding flat fees), and secure a concrete quote.
Keep it compact (4-6 total conversational exchanges).
Also, output the final quote details and amount at the bottom of the JSON.

Return the result strictly as a JSON object with this exact structure:
{
  "transcript": "AI Agent: Hello...\\nVendor: Hi...\\nAI Agent: ...",
  "quote": {
    "amount": 450.00,
    "details": {
      "breakdown": "Flat rate quote",
      "availability": "Confirmed for next Friday",
      "guarantees": "Included basic cargo protection"
    }
  }
}`;

      const response = await ai.models.generateContent({
        model: "gemini-2.5-flash",
        contents: prompt,
        config: {
          responseMimeType: "application/json",
          temperature: 0.7,
        }
      });

      return NextResponse.json(JSON.parse(response.text || "{}"));
    }

    return NextResponse.json({ error: "Unknown action" }, { status: 400 });
  } catch (error: any) {
    console.error("Gemini API Error:", error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
