# NavCore — Video Script

---

**[OPENING — 0:00]**

A few months back, I was standing inside a large hospital in Pune,
trying to find the Cardiology department.

There was no one around to guide me.
I kept walking down corridors, checking signboards, asking random people.

At that moment I thought — we are living in the age of AI.
So why does navigating a hospital still require chasing down a security guard?

That's when I started building NavCore.

---

**[WHAT IT IS — 0:20]**

NavCore is a fully offline AI hospital navigation system.

You can walk up to it and type what you're looking for.
You can talk to it naturally in Hindi, Marathi, or English.
You can even scan a QR code on the wall.

And the entire pipeline starts working — without making a single cloud or API call.

---

**[THE PROBLEM WITH EXISTING SYSTEMS — 0:40]**

Most hospital navigation systems do keyword matching.
You search for "Cardiology" and it finds "Cardiology."
But if you say "dil ke doctor kahaan hain" — it returns nothing.

Because it's looking for the exact word, not the meaning.

NavCore performs semantic retrieval instead.
It understands intent — not just keywords.

---

**[THE PIPELINE — 1:00]**

Here's how it works.

First, your query — text, voice, or QR scan — flows into a 7-node LangGraph workflow.

Node 2 automatically detects your language.
Hindi, Marathi, English, or code-mixed Hinglish.
No language selection needed. It just knows.

Node 4 embeds your query using multilingual-e5-small —
a 117MB model that maps Hindi, Marathi, and English into the same vector space.
That query vector is then searched inside Qdrant Edge,
which runs completely locally as a file — no server, no port, no network.

Whether you typed "dil ke doctor" or "cardiologist" or "hriday rog visheshagya" —
all of them map to the same embedding, and all of them find Cardiology OPD.

Node 6 then runs BFS on a topological graph of the hospital.
The LLM never decides the path. The graph does.
This is important — because LLMs fail at junction choices 59% of the time.
By using deterministic BFS, we eliminate that failure entirely.

Finally, Node 7 sends the computed path to Llama 3.2 3B running via Ollama —
locally, offline — which translates the path into natural spoken directions
in the patient's language.

---

**[DEMO — TEXT QUERIES — 1:45]**

Let me show you.

[Show terminal / NavCore interface]

English — "where is cardiology" —
Path: main entrance, lift A, floor 3 corridor, Cardiology OPD. 4 steps.

Hindi — "dil ke doctor kahaan hain" —
Same destination. Detected as Hinglish. Directions generated in Hindi.

Marathi — full Devanagari — still works.
No translation API. The embedding model handles it natively.

---

**[DEMO — VOICE — 2:10]**

Now voice.

[Show voice button being pressed]

I press the mic, say "baccho ka doctor kahaan hai" —
Whisper tiny runs locally, transcribes it in about 2 seconds —
and the workflow picks it up as a normal text query from there.

Whisper tiny is 39MB. Runs on any laptop CPU.
No cloud ASR. No Google, no Azure.

---

**[DEMO — QR CODE — 2:30]**

Every junction in the hospital has a QR code.

[Show QR scan on phone]

A patient scans the QR near Lift A on Floor 3.
NavCore instantly knows where they are.
The next query starts from Floor 3 — not the main entrance.
Shorter path. More accurate directions.

And it works on any smartphone. No app download required.
Just scan and the web NavCore interface opens with your location pre-set.

---

**[DEMO — MULTI-DESTINATION — 2:55]**

One more thing.

Real patients don't have just one stop.
They might need a blood test first, then see the cardiologist.

[Type: "pehle blood test phir Dr. Mehta se milna hai"]

One query. NavCore detects two destinations,
plans a sequential route — lab first, then Cardiology —
and gives combined step-by-step directions for the whole trip.

---

**[WHY OFFLINE — 3:20]**

Now — why does this need to be offline?

Three reasons.

Privacy. A patient's voice recording, query history, and location data
never leave the device. There's nothing to leak.

Reliability. Hospital Wi-Fi is notoriously bad.
A navcore that needs the internet will fail exactly when someone needs it most.
NavCore works even when the network is down.

Cost. No API bills. No per-query charges.
You deploy it once and it runs forever.

---

**[BENCHMARK — 3:45]**

I ran a proper benchmark — 200 queries across four languages.
Hindi, Marathi, English, and code-mixed Hinglish.
50 queries per language.

Three conditions: keyword baseline, flat semantic RAG, and NavCore.

Keyword matching gets 39% destination accuracy.
It fails completely on Hindi queries.

Flat semantic RAG gets 76% destination accuracy —
good retrieval, but the LLM has to guess the route.

NavCore gets 76% destination accuracy —
same retrieval quality — but 76% path accuracy and 90% junction accuracy.

That last number is the important one.
At every turn in the hospital, NavCore gets the direction right 90% of the time.
Flat RAG has zero junction accuracy because it never computes a path.

P50 latency is 355 milliseconds on CPU. No GPU needed.

---

**[CLOSING — 4:20]**

The real engineering challenge wasn't any single component.

It was getting Hindi voice input, multilingual embeddings,
deterministic graph search, and a local LLM to work together as one seamless pipeline —
while keeping everything offline, under 3 seconds, on cheap hospital hardware.

NavCore is fully open source.
All 129 tests pass. The benchmark numbers are real.

If you're building something for Indian physical spaces —
hospitals, colleges, train stations, malls —
the plugin architecture makes it trivial to swap in your own floor plan.

If you end up building something with it, I'd genuinely love to see it.

---

*[End card: GitHub link, benchmark results, demo video]*
