**Ep. 308 — How Image Diffusion Models Work - the 20 minute explainer**
*Fragmented · Kaushik & Yuri · 25 min · Mar 24, 2026*

A follow-up to their LLM explainer (ep. 303), Kaushik and Yuri walk through the full pipeline behind image diffusion models — from why raw pixels don't work as training input to how a text prompt ends up producing an image.

The core problem: images are already math (RGB pixels), but pixels don't carry semantic meaning the way token embeddings do. Feeding millions of raw pixels through attention is computationally infeasible. The solution is a **Variational AutoEncoder (VAE)**, which compresses an image into a **latent** — a compact grid of numbers that encodes the image's semantic content. Latents are to images what embeddings are to tokens: you can do math with them. Average two latents and you decode something visually between the two source images.

Training replaces the "predict the next token" mechanism with **noise scheduling across timesteps**. A real image gets progressively blurred until it's pure noise (time 0 = full noise, time T = clean image). The model learns to predict what noise to remove at each timestep — the Michelangelo analogy lands well here: you start with a block of marble and learn what to chip away. The final piece is **text conditioning**: training data pairs each image with a text caption, both converted to embeddings and trained together. That's the bridge from "user types a prompt" to "model generates a matching image."

**Why it's worth your time:** If you've internalized how LLMs work but image models still feel like magic, this episode closes that gap efficiently. The noise-as-time-dimension insight — and how it parallels next-token prediction — makes the whole architecture click.