# 🎧 Model Card: Applied AI Music Recommender System

## 1. Model Name

VibeFinder 2.0 RAG Enhanced Edition

---

## 2. Base Project and Original Scope

This system extends the Music Recommender Simulation from Module 3 (AI110). The original system used a weighted scoring function to rank a 20-song CSV catalog against a user preference profile across four features: genre, mood, energy, and acousticness. It returned rule-based explanations tied directly to the scoring logic and was tested across six user profiles (three standard, three adversarial) via a Python CLI.

---

## 3. New AI Features Added

**Retrieval-Augmented Generation (RAG):** A knowledge base of 10 genre description documents is retrieved at query time based on the user's preferred genre. The retrieved text is passed to the Gemini API alongside the song data and user preferences, grounding the AI explanation in real musical context rather than scoring math.

**Input Validation Guardrails:** A validation layer checks all four profile fields before reaching the recommender. Hard errors (invalid energy range, unrecognized genre/mood) block execution. Soft warnings (conflicting preferences like ambient combined with high energy) allow execution but surface the issue to the user.

**Automated Evaluation Harness:** `src/evaluator.py` runs 6 predefined test cases covering scoring correctness and guardrail behavior, then prints a pass/fail summary.

---

## 4. How the System Works

A user profile with four values (genre, mood, energy, likes_acoustic) enters the system. Guardrails validate the profile. If valid, the recommender scores all 20 songs using the same weighted function as the original system. Simultaneously, the RAG module loads the genre knowledge document and builds a context string combining it with the user's preferences. The explainer passes the top-k songs, their rule-based scores, and the RAG context to Gemini, which returns 2 to 3 sentence natural-language explanations. If the API is unavailable, the system falls back to the rule-based explanation string.

---

## 5. Data

The song catalog is unchanged from Module 3: 20 songs across 12 genres and 6 moods, each with 8 attributes. The knowledge base is 10 plain-text files (one per genre or genre group) written to describe the typical musical characteristics, listener use cases, energy profiles, and cultural context of each genre. These documents were written to complement the scoring function. For example, the ambient.txt document explicitly notes that ambient and high-energy are incompatible, which informs the conflict warning in the guardrails.

---

## 6. Strengths

The RAG-enhanced explanations are meaningfully more useful than the original rule-based strings. A user reading "Sunrise City fits you, it is an upbeat pop track with high energy and a happy mood, exactly the kind of polished, danceable sound pop listeners gravitate toward" understands the recommendation better than reading "genre match: pop (+3.0); mood match: happy (+2.0)." The guardrail system catches the most common failure modes before they silently produce bad results. The fallback mechanism means the system is independently functional without cloud dependencies.

---

## 7. Limitations and Bias

The catalog sparsity problem from Module 3 is unchanged. Genres with only one song produce one good recommendation followed by weak fallbacks. The RAG retrieval is exact-match on genre, so if a genre is not in the knowledge base map it gets no context, which degrades explanation quality for edge cases. The Gemini explanations are only as grounded as the knowledge base documents, so if a document contains inaccuracies the AI will confidently repeat them. The system still treats all users as having static preferences with no feedback loop.

---

## 8. Ethical Considerations

Mood and genre preference inference from user-provided profiles is low-risk in a music context, but the same architecture applied to higher-stakes domains (hiring, lending, health) would require much stronger guardrails and bias auditing. The conflict detection in this system is a lightweight example of what responsible AI design looks like at scale: surfacing system limitations to the user rather than silently producing outputs that do not serve them.

---

## 9. Evaluation

Six test cases were run through the evaluation harness. Three tested whether the correct genre appeared at rank 1 for standard profiles (pop, lofi, edm) and all three passed. Two tested whether invalid profiles were correctly blocked by guardrails (energy=1.8 and unrecognized genre "bossa nova") and both passed. One tested the niche-genre case (country) and passed. Final result: 6/6.

The most surprising finding was that the guardrail conflict warning for the Riley profile (ambient combined with high energy) improved the user experience even though the recommendations themselves were unchanged. Making the system's limitations visible turned a confusing result into an understandable one.

---

## 10. AI Collaboration Reflection

AI was used throughout this project for drafting the knowledge base documents, structuring the RAG context prompt, and debugging the fallback logic in the explainer. The most helpful suggestion was the prompt structure for the Gemini API call. Separating the genre knowledge section, the user preferences section, and the rule-based reasons into clearly labeled blocks gave Gemini enough context to produce specific, accurate explanations. The most flawed suggestion was an early recommendation to implement TF-IDF cosine similarity for retrieval across the 10 knowledge base documents, which would have added significant complexity (scikit-learn dependency, index management, tuning) for a dataset small enough that a dictionary lookup is both faster and more transparent.

---

## 11. Future Work

1. Expand the catalog to at least 5 songs per genre so niche listeners get meaningful ranked results.
2. Replace exact-match genre retrieval with semantic similarity so adjacent genres (for example "indie folk" retrieving both folk and indie pop docs) get richer context.
3. Add a feedback loop where users can rate recommendations and the system adjusts weights over sessions.