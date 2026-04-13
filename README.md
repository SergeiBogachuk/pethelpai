# Pet Help AI MVP

Streamlit MVP for `pethelpai.com`.

## What is included

- pet profile editor for dog or cat
- AI behavior coach for common dog and cat behavior issues
- same-day action plan plus 7-day routine guidance
- optional AI image understanding of the pet setup when `OPENAI_API_KEY` is available
- simple history and personalized routine plan

## Run locally

From the workspace root:

```bash
python3 -m streamlit run pethelpai/app.py
```

Optional environment variables:

```bash
export OPENAI_API_KEY="your-key"
export OPENAI_MODEL="gpt-4.1-mini"
```

Without `OPENAI_API_KEY`, the app still works with manual descriptions and behavior text input.

## Logo placement

If you want the app to show your brand logo automatically, put one of these files into:

`assets/`

Supported filenames:

- `assets/logo.svg`
- `assets/logo.png`
- `assets/logo.webp`
- `assets/logo.jpg`
- `assets/logo.jpeg`

The app will auto-detect the first one it finds and use it in the header and sidebar.

## Recommended deploy flow

This workspace contains multiple unrelated projects, so the cleanest production path is:

1. Create a dedicated GitHub repository for the contents of this `pethelpai/` folder.
2. Push only these files into that repo root:
   - `app.py`
   - `engine.py`
   - `styles.py`
   - `requirements.txt`
   - `render.yaml`
   - `.gitignore`
3. Create a Render web service from that GitHub repo.
4. Add `OPENAI_API_KEY` in Render environment variables.
5. Connect the custom domain `pethelpai.com` in Render.

## Render notes

- Build command: already defined in `render.yaml`
- Start command: already defined in `render.yaml`
- Custom domain: add it in Render first, then copy the DNS records Render gives you into your domain provider

## Production recommendation

For the fastest launch, point the root domain directly to the app:

- `pethelpai.com` -> Streamlit app

Later, if you want a fuller marketing experience, split it into:

- `pethelpai.com` -> landing page
- `app.pethelpai.com` -> application
