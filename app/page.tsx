export default function Home() {
  return (
    <main className="min-h-screen flex items-center justify-center bg-background text-foreground px-6">
      <div className="max-w-xl text-center space-y-4">
        <h1 className="text-4xl font-semibold tracking-tight">Price Negotiator API</h1>
        <p className="text-muted-foreground">
          The frontend UI lives in the separate [frontend](../frontend) app. This backend app is for API and agent processing only.
        </p>
      </div>
    </main>
  );
}
                  <p className="font-sans text-xs text-zinc-400 leading-relaxed">
                    Test the system instantly. The workspace automatically proxies to Gemini and runs dynamic simulations if background service container hooks are offline.
                  </p>
                </div>
              </div>
            </motion.section>
          ) : (
            /* Phase 2: Active Workspace Dashboard */
            <motion.div 
              key="workspace-dashboard"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="grid lg:grid-cols-12 gap-6 items-start"
            >
              
              {/* Left Column: Flow Details & Form */}
              <div className="lg:col-span-7 space-y-6">
                
                {/* Active Chat Interview Flow (If incomplete) */}
                {!state.requirement?.is_complete && (
                  <section className="bg-zinc-900/40 border border-amber-900/30 rounded-2xl p-6 space-y-4">
                    <div className="flex items-start gap-3">
                      <div className="w-8 h-8 rounded-lg bg-amber-950/50 border border-amber-500/50 flex items-center justify-center text-amber-400">
                        <User className="w-4 h-4" />
                      </div>
                      <div className="space-y-1">
                        <span className="font-mono text-[10px] text-amber-400 uppercase tracking-widest">Intake Interview Agent</span>
                        <p className="text-zinc-200 text-sm font-sans leading-relaxed">
                          {state.requirement?.follow_up_question}
                        </p>
                      </div>
                    </div>

                    <form onSubmit={handleStart} className="flex gap-2">
                      <input
                        placeholder="Add more details to complete your request..."
                        value={prompt}
                        onChange={(e) => setPrompt(e.target.value)}
                        className="flex-1 bg-zinc-950 border border-zinc-800 rounded-xl px-4 py-2 text-sm text-zinc-200 placeholder-zinc-600 focus:outline-none focus:border-amber-500 transition font-sans"
                      />
                      <button
                        type="submit"
                        disabled={loading}
                        className="bg-amber-500 hover:bg-amber-600 text-zinc-950 px-4 py-2 rounded-xl text-sm font-sans font-bold flex items-center gap-1.5 transition"
                      >
                        <Send className="w-3.5 h-3.5" />
                        Reply
                      </button>
                    </form>
                  </section>
                )}

                {/* Strategy Bento & Focus Areas */}
                {state.call_plan && (
                  <section className="bg-zinc-900/40 border border-zinc-850 rounded-2xl p-5 md:p-6 space-y-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2 text-cyan-400">
                        <Cpu className="w-4 h-4" />
                        <h4 className="font-sans font-bold text-sm">Autonomous Negotiation Strategy</h4>
                      </div>
                      <span className="font-mono text-[9px] text-zinc-500 border border-zinc-850 px-2 py-0.5 rounded bg-zinc-950">
                        GENERATED PLAN
                      </span>
                    </div>
                    <div className="space-y-4">
                      <p className="text-zinc-300 text-xs italic font-sans leading-relaxed border-l-2 border-cyan-500 pl-4 py-1 bg-cyan-950/10">
                        &ldquo;{state.call_plan.strategy}&rdquo;
                      </p>
                      <div className="space-y-2">
                        <h5 className="font-mono text-[10px] text-zinc-500 tracking-wider">TARGET FOCUS AREAS:</h5>
                        <div className="flex flex-wrap gap-2">
                          {state.call_plan.focus_areas.map((area, idx) => (
                            <span key={idx} className="font-sans text-xs bg-zinc-950 border border-zinc-800 text-zinc-400 px-3 py-1 rounded-full">
                              🎯 {area}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  </section>
                )}

                {/* Live Transcript / Calling Node Details */}
                {state.calls && state.calls.length > 0 && (
                  <section className="bg-zinc-900/40 border border-zinc-850 rounded-2xl overflow-hidden">
                    <div className="p-5 border-b border-zinc-850 flex items-center justify-between bg-zinc-900/20">
                      <div className="flex items-center gap-2">
                        <span className="relative flex h-2 w-2">
                          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
                          <span className="relative inline-flex rounded-full h-2 w-2 bg-cyan-500"></span>
                        </span>
                        <h4 className="font-sans font-bold text-sm text-zinc-200">Voice Call & Transcription Desk</h4>
                      </div>
                      <span className="font-mono text-[10px] text-zinc-500">SIMULATION ENGINE ACTIVE</span>
                    </div>

                    <div className="flex border-b border-zinc-850 font-mono text-xs bg-zinc-950/50">
                      {state.calls.map((call, idx) => {
                        const biz = state.candidate_businesses.find(b => b.business_id === call.business_id);
                        const isActive = idx === activeCallIndex;
                        return (
                          <button
                            key={call.call_id}
                            onClick={() => setActiveCallIndex(idx)}
                            className={`flex-1 py-3 px-4 text-center border-r border-zinc-850 transition ${
                              isActive 
                                ? "bg-zinc-900 text-cyan-400 font-bold border-b-2 border-b-cyan-500" 
                                : "text-zinc-500 hover:text-zinc-350"
                            }`}
                          >
                            📞 {biz?.name || `Provider ${idx + 1}`}
                          </button>
                        );
                      })}
                    </div>

                    <div className="p-5 space-y-4 bg-zinc-950/60 font-mono text-xs">
                      {state.calls[activeCallIndex] ? (
                        <div className="space-y-4">
                          <div className="flex items-center justify-between border-b border-zinc-900 pb-3">
                            <span className="text-zinc-500">
                              STATUS: <span className={state.calls[activeCallIndex].status === "completed" ? "text-green-400" : "text-cyan-400 animate-pulse"}>
                                {state.calls[activeCallIndex].status.toUpperCase()}
                              </span>
                            </span>
                            <span className="text-zinc-500">
                              OUTCOME: <span className="text-zinc-350">{state.calls[activeCallIndex].outcome}</span>
                            </span>
                          </div>

                          {/* Animated voice wave for realism */}
                          {state.calls[activeCallIndex].status !== "completed" && (
                            <div className="flex items-center justify-center gap-1.5 py-6">
                              {[1, 2, 3, 4, 5, 4, 3, 2, 1, 2, 3, 4, 3, 2, 1].map((h, i) => (
                                <span 
                                  key={i} 
                                  className="w-1 bg-cyan-400/80 rounded-full animate-bounce" 
                                  style={{ 
                                    height: `${h * 4}px`, 
                                    animationDelay: `${i * 150}ms`,
                                    animationDuration: "1s" 
                                  }}
                                ></span>
                              ))}
                              <span className="ml-3 text-cyan-400 text-[10px] animate-pulse">NEGOTIATING RATES...</span>
                            </div>
                          )}

                          {state.calls[activeCallIndex].transcript ? (
                            <div className="space-y-3 bg-zinc-900/50 p-4 rounded-xl border border-zinc-900 leading-relaxed h-64 overflow-y-auto">
                              <p className="text-zinc-500 italic mb-2">{"// SECURE VOICE TRANSCRIPT LOG"}</p>
                              <div className="whitespace-pre-line text-zinc-300 font-sans">
                                {state.calls[activeCallIndex].transcript}
                              </div>
                            </div>
                          ) : (
                            <p className="text-center py-6 text-zinc-500 italic">Dialing phone lines. Real-time transcript starting shortly...</p>
                          )}
                        </div>
                      ) : (
                        <p className="text-center py-6 text-zinc-500">Gathering information to initiate dialing engine...</p>
                      )}
                    </div>
                  </section>
                )}

              </div>

              {/* Right Column: Comparison Table, Recommendation & Approval */}
              <div className="lg:col-span-5 space-y-6">
                
                {/* Discovered Businesses list */}
                {state.candidate_businesses && state.candidate_businesses.length > 0 && (
                  <section className="bg-zinc-900/40 border border-zinc-850 rounded-2xl p-5 md:p-6 space-y-4">
                    <div className="flex items-center gap-2 text-cyan-400">
                      <Search className="w-4 h-4" />
                      <h4 className="font-sans font-bold text-sm">Discovered Business Contacts</h4>
                    </div>

                    <div className="space-y-3">
                      {state.candidate_businesses.map((biz, idx) => (
                        <div key={biz.business_id} className="flex items-center justify-between p-3.5 rounded-xl border border-zinc-850 bg-zinc-950/60">
                          <div className="space-y-1">
                            <h5 className="font-sans font-bold text-xs text-zinc-200">{biz.name}</h5>
                            <div className="flex items-center gap-2 font-mono text-[10px] text-zinc-500">
                              <MapPin className="w-3 h-3 text-zinc-600" />
                              <span>{biz.phone}</span>
                            </div>
                          </div>
                          <div className="flex items-center gap-1 bg-zinc-900 px-2.5 py-1 rounded border border-zinc-800">
                            <Star className="w-3 h-3 text-amber-400 fill-amber-400" />
                            <span className="font-mono text-xs text-amber-400">{biz.rating || "4.5"}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </section>
                )}

                {/* Quotes Comparative Matrix */}
                {state.quote_comparison && (
                  <section className="bg-zinc-900/40 border border-zinc-850 rounded-2xl p-5 md:p-6 space-y-4">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2 text-cyan-400">
                        <Layers className="w-4 h-4" />
                        <h4 className="font-sans font-bold text-sm">Decision-Support Matrix</h4>
                      </div>
                      <span className="font-mono text-[9px] text-zinc-500 border border-zinc-800 px-2 py-0.5 rounded bg-zinc-950">
                        COMPARATIVE RATES
                      </span>
                    </div>

                    <div className="overflow-x-auto rounded-xl border border-zinc-850">
                      <table className="w-full font-sans text-xs">
                        <thead>
                          <tr className="bg-zinc-950 font-mono text-zinc-500 border-b border-zinc-850">
                            <th className="py-2.5 px-3 text-left">PROVIDER</th>
                            <th className="py-2.5 px-3 text-right">RATING</th>
                            <th className="py-2.5 px-3 text-right">PRICE</th>
                          </tr>
                        </thead>
                        <tbody>
                          {Object.entries(state.quote_comparison.comparisons).map(([name, data]: any) => (
                            <tr key={name} className="border-b border-zinc-850 hover:bg-zinc-900/20">
                              <td className="py-3 px-3 font-semibold text-zinc-200">{name}</td>
                              <td className="py-3 px-3 text-right text-amber-400 font-mono">{data.rating} / 5.0</td>
                              <td className="py-3 px-3 text-right font-bold text-green-400 font-mono">${data.price}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </section>
                )}

                {/* Human Approval Gate */}
                {state.requires_human_approval && state.recommendation && (
                  <motion.section 
                    initial={{ scale: 0.95, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    className="border border-amber-500/30 bg-amber-500/5 rounded-2xl p-6 space-y-5 shadow-lg shadow-amber-500/5"
                  >
                    <div className="flex items-center gap-2.5 text-amber-500">
                      <ShieldAlert className="w-5 h-5" />
                      <h4 className="font-sans font-bold text-sm">Human Intervention Gate</h4>
                    </div>

                    <div className="space-y-4">
                      <div className="space-y-1 bg-zinc-950/80 p-4 rounded-xl border border-zinc-900">
                        <span className="font-mono text-[9px] text-zinc-500 uppercase">SYSTEM RECOMMENDATION</span>
                        <h5 className="font-sans font-bold text-sm text-zinc-200">
                          {state.candidate_businesses.find(b => b.business_id === state.recommendation?.recommended_business_id)?.name || "Recommended Provider"}
                        </h5>
                        <p className="text-zinc-400 text-xs mt-1.5 leading-relaxed font-sans">
                          {state.recommendation.reasoning}
                        </p>
                      </div>

                      <button
                        onClick={handleApprove}
                        disabled={loading}
                        className="w-full bg-amber-500 hover:bg-amber-600 text-zinc-950 font-sans font-bold py-3 px-6 rounded-xl transition flex items-center justify-center gap-2 text-sm shadow-lg shadow-amber-500/10"
                      >
                        {loading ? (
                          <>
                            <RefreshCw className="w-4 h-4 animate-spin" />
                            Finalizing Contract Documents...
                          </>
                        ) : (
                          <>
                            <ThumbsUp className="w-4 h-4" />
                            Approve & Execute Contract
                          </>
                        )}
                      </button>
                    </div>
                  </motion.section>
                )}

                {/* Final PDF Report & Download */}
                {state.status === "done" && (
                  <motion.section 
                    initial={{ y: 15, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    className="border border-green-500/30 bg-green-500/5 rounded-2xl p-6 space-y-5"
                  >
                    <div className="flex items-center gap-2 text-green-400">
                      <FileCheck2 className="w-5 h-5" />
                      <h4 className="font-sans font-bold text-sm">Contract Generation Complete</h4>
                    </div>

                    <div className="space-y-4">
                      {/* Visual savings meter */}
                      <div className="bg-zinc-950/80 p-4 rounded-xl border border-zinc-900 flex items-center justify-between">
                        <div className="space-y-1">
                          <span className="font-mono text-[9px] text-zinc-500 uppercase">NEGOTIATION OUTCOME</span>
                          <p className="text-zinc-200 text-sm font-sans font-bold">Contract Finalized & Signed</p>
                        </div>
                        <div className="text-right">
                          <span className="font-mono text-[10px] text-zinc-500 uppercase block">SAVINGS GENERATED</span>
                          <span className="text-green-400 font-mono text-lg font-bold">-$120.00 (24%)</span>
                        </div>
                      </div>

                      <button 
                        onClick={(e) => {
                          e.preventDefault();
                          downloadReport();
                        }}
                        className="w-full bg-green-500 hover:bg-green-600 text-zinc-950 font-sans font-bold py-3 px-6 rounded-xl transition flex items-center justify-center gap-2 text-sm shadow-lg shadow-green-500/10 cursor-pointer"
                      >
                        <Download className="w-4 h-4" />
                        Download Final Contract Report
                      </button>
                    </div>
                  </motion.section>
                )}

              </div>
              
            </motion.div>
          )}
        </AnimatePresence>

      </div>

      {/* Footer bar */}
      <footer className="border-t border-zinc-900 bg-zinc-950 py-8 mt-12 text-center text-zinc-600">
        <div className="max-w-7xl mx-auto px-4 font-mono text-[10px] space-y-1">
          <p>CONCENSUSAI MULTI-AGENT STATEFUL PIPELINE SYSTEM v1.2</p>
          <p>BUILT WITH FASTAPI, LANGGRAPH, CELERY, REDIS, AND GOOGLE AI STUDIO</p>
        </div>
      </footer>

    </main>
  );
}
