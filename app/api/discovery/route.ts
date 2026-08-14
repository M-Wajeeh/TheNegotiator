import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  try {
    const { service_type, location } = await req.json();

    if (!service_type || !location) {
      return NextResponse.json({ error: "Missing service_type or location" }, { status: 400 });
    }

    const apiKey = process.env.TAVILY_API_KEY;
    if (apiKey && apiKey !== "dummy-key-for-now" && apiKey.startsWith("tvly-")) {
      // Perform a real Tavily Search API call
      try {
        const query = `${service_type} in ${location} phone website rating`;
        const res = await fetch("https://api.tavily.com/search", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            api_key: apiKey,
            query,
            search_depth: "advanced",
            max_results: 5,
          }),
        });

        if (res.ok) {
          const data = await res.json();
          // Let's use Gemini to parse these search results into a structured Business list!
          // We can do it here or let the client handle it. Let's do it in this API route to keep it clean.
          return NextResponse.json({ results: data.results });
        }
      } catch (searchError) {
        console.error("Tavily real search failed, falling back:", searchError);
      }
    }

    // High-quality mock responses tailored to the user's specific request
    const mockBusinesses = [
      {
        business_id: "biz-1",
        name: `Elite ${service_type} of ${location}`,
        phone: "(212) 555-8902",
        website: `https://elite${service_type.toLowerCase().replace(/\s+/g, "")}.com`,
        rating: 4.8
      },
      {
        business_id: "biz-2",
        name: `Metro ${service_type} Pros`,
        phone: "(718) 555-4431",
        website: `https://metro${service_type.toLowerCase().replace(/\s+/g, "")}pros.com`,
        rating: 4.6
      },
      {
        business_id: "biz-3",
        name: `Precision ${service_type} Co.`,
        phone: "(917) 555-0199",
        website: `https://precision${service_type.toLowerCase().replace(/\s+/g, "")}.com`,
        rating: 4.9
      }
    ];

    return NextResponse.json({ results: null, mock: mockBusinesses });
  } catch (error: any) {
    console.error("Discovery API Error:", error);
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
