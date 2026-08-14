import { NextRequest, NextResponse } from "next/server";
import { GoogleGenAI, Type } from "@google/genai";

const ai = new GoogleGenAI({
  apiKey: process.env.GEMINI_API_KEY,
  httpOptions: {
    headers: {
      "User-Agent": "aistudio-build",
    },
  },
});

// In-memory state store for the preview simulation fallback
// Real applications persist this in DB, but since the preview container starts fresh,
// we can keep a robust in-memory store for immediate interactive testing.
const simulatedStates: Record<string, any> = {};

// Helper to check if local FastAPI backend is active
async function isBackendAlive(): Promise<boolean> {
  try {
    const res = await fetch("http://localhost:8000/health", { signal: AbortSignal.timeout(1000) });
    return res.ok;
  } catch {
    return false;
  }
}

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { action, id, details, fileBase64, filename } = body;

    const backendActive = await isBackendAlive();

    if (backendActive) {
      // Proxy to Python FastAPI Backend
      if (action === "start") {
        const response = await fetch("http://localhost:8000/negotiations/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ dummy_payload: details }),
        });
        const data = await response.json();
        return NextResponse.json({ ...data, is_simulated: false });
      }

      if (action === "approve") {
        const response = await fetch(`http://localhost:8000/negotiations/${id}/approve`, {
          method: "POST",
        });
        const data = await response.json();
        return NextResponse.json({ ...data, is_simulated: false });
      }

      if (action === "get_status") {
        const response = await fetch(`http://localhost:8000/negotiations/${id}`);
        const data = await response.json();
        return NextResponse.json({ state: data, is_simulated: false });
      }
    }

    // --- FALLBACK HIGH-FIDELITY GEMINI-POWERED STATEFUL SIMULATOR ---
    if (action === "start") {
      const negotiationId = id || crypto.randomUUID();
      
      // If a document is uploaded, we parse it using Gemini vision capabilities
      let parsedDoc = null;
      if (fileBase64 && filename) {
        try {
          const base64Data = fileBase64.split(",")[1] || fileBase64;
          const visionPrompt = "Extract key details from this document. What is the business name, the total amount, and summary details?";
          const visionResponse = await ai.models.generateContent({
            model: "gemini-3.5-flash",
            contents: [
              {
                inlineData: {
                  mimeType: "image/jpeg",
                  data: base64Data,
                },
              },
              { text: visionPrompt },
            ],
            config: {
              responseMimeType: "application/json",
              responseSchema: {
                type: Type.OBJECT,
                properties: {
                  business_name: { type: Type.STRING },
                  total_amount: { type: Type.NUMBER },
                  extracted_details: {
                    type: Type.OBJECT,
                    properties: {
                      issue: { type: Type.STRING },
                      items: { type: Type.STRING },
                    },
                  },
                },
              },
            },
          });

          const visionResult = JSON.parse(visionResponse.text || "{}");
          parsedDoc = {
            filename,
            business_name: visionResult.business_name || "Unknown Company",
            total_amount: visionResult.total_amount || 0,
            extracted_details: visionResult.extracted_details || {},
          };
        } catch (visionErr) {
          console.error("Gemini Vision Parsing failed:", visionErr);
          parsedDoc = {
            filename,
            business_name: "Apex Handyman Services",
            total_amount: 450.0,
            extracted_details: { service: "Pipe repair", date: "2026-07-20" },
          };
        }
      }

      // 1. Core Intake Agent Logic: Analyze user input for completeness
      const systemPrompt = `You are an expert Negotiation Intake Agent. Your job is to analyze the user's service requirements.
Determine if the input contains:
1. Service Type (e.g., plumber, mover, lawyer)
2. Location/City
3. Specific parameters (size of move, urgency, details).

If incomplete, set is_complete to false and generate a supportive follow-up question.
If complete, set is_complete to true and extract the details.`;

      const geminiResponse = await ai.models.generateContent({
        model: "gemini-3.5-flash",
        contents: `Analyze the following user input: "${details.prompt}"`,
        config: {
          systemInstruction: systemPrompt,
          responseMimeType: "application/json",
          responseSchema: {
            type: Type.OBJECT,
            properties: {
              is_complete: { type: Type.BOOLEAN },
              service_type: { type: Type.STRING },
              location: { type: Type.STRING },
              follow_up_question: { type: Type.STRING },
              extracted_parameters: {
                type: Type.OBJECT,
                properties: {
                  urgency: { type: Type.STRING },
                  description: { type: Type.STRING },
                },
              },
            },
          },
        },
      });

      const intakeResult = JSON.parse(geminiResponse.text || "{}");

      const initialState: any = {
        negotiation_id: negotiationId,
        status: intakeResult.is_complete ? "discovering" : "intake",
        requirement: {
          service_type: intakeResult.service_type || null,
          location: intakeResult.location || null,
          is_complete: intakeResult.is_complete || false,
          follow_up_question: intakeResult.follow_up_question || null,
          details: intakeResult.extracted_parameters || {},
        },
        parsed_documents: parsedDoc ? [parsedDoc] : [],
        candidate_businesses: [],
        call_plan: null,
        calls: [],
        quotes: [],
        quote_comparison: null,
        recommendation: null,
        report_url: null,
        requires_human_approval: false,
        is_simulated: true,
      };

      simulatedStates[negotiationId] = initialState;

      // If requirements are complete, run the background steps sequentially
      if (intakeResult.is_complete) {
        // Run full simulation in background
        runSimulatedPipeline(negotiationId, intakeResult.service_type, intakeResult.location);
      }

      return NextResponse.json({ negotiation_id: negotiationId, is_simulated: true, state: initialState });
    }

    if (action === "approve") {
      const state = simulatedStates[id];
      if (!state) {
        return NextResponse.json({ error: "Negotiation not found" }, { status: 404 });
      }

      state.status = "reporting";
      state.requires_human_approval = false;

      // Generate report url and complete pipeline
      setTimeout(() => {
        state.status = "done";
        state.report_url = `https://negotiation-platform-reports.s3.amazonaws.com/${id}_summary.pdf`;
      }, 2000);

      return NextResponse.json({ status: "resumed", is_simulated: true });
    }

    if (action === "get_status") {
      const state = simulatedStates[id];
      if (!state) {
        return NextResponse.json({ error: "Negotiation not found" }, { status: 404 });
      }
      return NextResponse.json({ state, is_simulated: true });
    }

    return NextResponse.json({ error: "Invalid action" }, { status: 400 });
  } catch (error: any) {
    console.error("API Route Error:", error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}

// Background simulation runner
async function runSimulatedPipeline(id: string, serviceType: string, location: string) {
  const state = simulatedStates[id];
  if (!state) return;

  // Step 1: Business Discovery (takes 2 seconds)
  await sleep(2000);
  state.status = "discovering";
  
  // Use Gemini to discover candidate businesses realistically
  try {
    const discoveryPrompt = `Generate exactly 3 realistic, high-quality candidate businesses for the service: "${serviceType}" in "${location}".
For each business, provide:
1. A unique ID
2. Business name
3. Valid phone number
4. Overall rating (e.g. 4.7)
5. A realistic website link`;

    const response = await ai.models.generateContent({
      model: "gemini-3.5-flash",
      contents: discoveryPrompt,
      config: {
        responseMimeType: "application/json",
        responseSchema: {
          type: Type.OBJECT,
          properties: {
            candidates: {
              type: Type.ARRAY,
              items: {
                type: Type.OBJECT,
                properties: {
                  business_id: { type: Type.STRING },
                  name: { type: Type.STRING },
                  phone: { type: Type.STRING },
                  website: { type: Type.STRING },
                  rating: { type: Type.NUMBER },
                },
              },
            },
          },
        },
      },
    });

    const parsed = JSON.parse(response.text || "{}");
    state.candidate_businesses = parsed.candidates || [];
  } catch (e) {
    state.candidate_businesses = [
      { business_id: "biz-1", name: `Apex ${serviceType}`, phone: "555-0192", rating: 4.8, website: `apex-${serviceType.toLowerCase().replace(/[^a-z]/g, "")}.com` },
      { business_id: "biz-2", name: `Summit Contractors`, phone: "555-0243", rating: 4.5, website: "summitcontracting.com" },
      { business_id: "biz-3", name: `ProCare Solutions`, phone: "555-0811", rating: 4.2, website: "procaresolutions.net" },
    ];
  }

  // Step 2: Call Planning (takes 2 seconds)
  await sleep(2000);
  state.status = "planning";

  try {
    const planningPrompt = `Generate a strategic calling plan and focus areas for negotiating: "${serviceType}" in "${location}". 
Include:
1. Strategy (e.g. bundle services, request volume discount, highlight competitive quotes)
2. Focus areas (e.g. arrival speed, warranty period, transparent pricing)`;

    const response = await ai.models.generateContent({
      model: "gemini-3.5-flash",
      contents: planningPrompt,
      config: {
        responseMimeType: "application/json",
        responseSchema: {
          type: Type.OBJECT,
          properties: {
            strategy: { type: Type.STRING },
            focus_areas: {
              type: Type.ARRAY,
              items: { type: Type.STRING },
            },
          },
        },
      },
    });

    const parsedPlan = JSON.parse(response.text || "{}");
    state.call_plan = {
      strategy: parsedPlan.strategy || "Negotiate based on prompt availability and warranty period.",
      max_calls: 3,
      focus_areas: parsedPlan.focus_areas || ["Hourly Rate", "Travel Fees", "Warranty details"],
    };
  } catch (e) {
    state.call_plan = {
      strategy: "Leverage multi-vendor comparisons to demand a price match on diagnostic fees.",
      max_calls: 3,
      focus_areas: ["Base fee", "Hourly labor rate", "Written guarantee on parts"],
    };
  }

  // Step 3: Voice Calling & Telephony Simulation (staggered, 3 seconds each)
  state.status = "calling";
  
  for (let i = 0; i < state.candidate_businesses.length; i++) {
    await sleep(2000);
    const biz = state.candidate_businesses[i];
    
    // Simulate active calling status
    state.calls.push({
      business_id: biz.business_id,
      call_id: `call-${i}-${Date.now()}`,
      status: "calling",
      outcome: "IN_PROGRESS",
    });

    await sleep(2000);

    // Simulate complete transcript and quote extraction using Gemini
    let quoteAmount = 300 + Math.floor(Math.random() * 250);
    let transcriptText = "";

    try {
      const transcriptPrompt = `Generate a short realistic telephone negotiation transcript between our AI Negotiation Agent (representing the client) and ${biz.name} (${serviceType} provider). 
The AI agent must negotiate politely using the strategy: "${state.call_plan?.strategy}".
The business should quote an initial price, the AI agent should negotiate, and they should agree on a final amount of around $${quoteAmount}.
Include 4-5 dialogue lines.`;

      const response = await ai.models.generateContent({
        model: "gemini-3.5-flash",
        contents: transcriptPrompt,
      });
      transcriptText = response.text || "Connection completed successfully.";
    } catch (e) {
      transcriptText = `Agent: Hello, I'm calling to secure a competitive quote for ${serviceType} services in ${location}.
${biz.name}: Sure! Our standard rate is $450 for the first two hours.
Agent: We are comparing multiple bids today. Can you offer a volume discount or waive travel fees?
${biz.name}: We can waive the $50 dispatch fee, bringing the total to $400.
Agent: Excellent, we will add your finalized quote to our decision matrix.`;
    }

    // Update Call Status to completed
    const activeCall = state.calls.find((c: any) => c.business_id === biz.business_id);
    if (activeCall) {
      activeCall.status = "completed";
      activeCall.outcome = "CONFIRMED_QUOTE";
      activeCall.transcript = transcriptText;
    }

    // Add Quote
    state.quotes.push({
      business_id: biz.business_id,
      amount: quoteAmount,
      details: {
        warranty: "1 year standard",
        availability: "Same-day",
        discount_applied: "Waived dispatch fees",
      },
    });
  }

  // Step 4: Quote Analysis (takes 2 seconds)
  await sleep(2000);
  state.status = "analyzing";

  const comparisons: Record<string, any> = {};
  state.candidate_businesses.forEach((biz: any) => {
    const quote = state.quotes.find((q: any) => q.business_id === biz.business_id);
    comparisons[biz.name] = {
      price: quote ? quote.amount : 500,
      rating: biz.rating,
      availability: "Within 24 Hours",
      guarantee: "100% Satisfaction",
    };
  });

  state.quote_comparison = { comparisons };

  // Step 5: Recommendation & Human Gate (takes 2 seconds)
  await sleep(2000);
  state.status = "negotiating"; // Transition status
  
  // Sort quotes to find best recommendation
  const sortedQuotes = [...state.quotes].sort((a, b) => a.amount - b.amount);
  const recommendedBiz = state.candidate_businesses.find((b: any) => b.business_id === sortedQuotes[0]?.business_id) || state.candidate_businesses[0];

  state.recommendation = {
    recommended_business_id: recommendedBiz.business_id,
    reasoning: `Recommended ${recommendedBiz.name} because they offered the lowest bid of $${sortedQuotes[0]?.amount} with high rating (${recommendedBiz.rating}/5.0) and waived standard dispatch fees.`,
  };

  state.status = "recommending";
  state.requires_human_approval = true;
}

function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
