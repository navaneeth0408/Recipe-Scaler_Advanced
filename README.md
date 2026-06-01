# Recipe Scaler 🍳

A modular client-server application designed to extract, parse, and scale recipes from YouTube videos and raw text with AI-powered enhancements.

## What It Does
Recipe Scaler automates the tedious parts of cooking from digital sources. It allows users to search for recipes on YouTube, automatically extract ingredient lists from video metadata or descriptions, and parse them into structured data. Once structured, recipes can be scaled to any number of servings instantly. The platform integrates advanced AI to provide ingredient substitutions, nutritional insights, and a dedicated cooking assistant to handle real-time culinary queries.

## Features
- **YouTube Integration:** Search for recipes and extract metadata/ingredients directly from video URLs.
- **Structured Parsing:** Intelligent regex and AI-driven parsing of complex ingredient lists into quantities, units, and items.
- **Dynamic Scaling:** Adjust recipe quantities for any serving size with precise calculations.
- **AI Culinary Suite:**
  - **Substitutions:** Get smart alternatives for missing ingredients.
  - **Nutrition Analysis:** Automated nutritional breakdown of recipe components.
  - **Assistant Chat:** Context-aware AI to answer cooking and technique questions.
  - **Translation:** Localize recipes into multiple languages.
- **Robust Architecture:** Clean separation between a lightweight Vanilla JS frontend and a high-performance FastAPI backend.

## Tech Stack
| Layer | Technologies |
| :--- | :--- |
| **Frontend** | HTML5, Vanilla CSS3, Vanilla JavaScript |
| **Backend** | Python, FastAPI, Pydantic, SQLAlchemy |
| **Database** | MongoDB (Motor), SQLite (SQLAlchemy) |
| **AI / NLP** | OpenAI, LangChain, Groq, Spacy, Whisper (Audio Extraction) |
| **Integrations** | YouTube Data API, yt-dlp, Google API Client |
| **Utilities** | Deep-translator, HTTpx, Python-dotenv |

## How It Works
The application uses a modular client-server architecture where the frontend serves as a thin UI layer, and the backend handles all heavy processing through a series of specialized services.

```text
+-------------------+       +------------------------+       +-----------------------+
|   Web Frontend    |       |   FastAPI Backend      |       |   External Services   |
| (HTML/CSS/JS)     | <---> | (Business Logic)       | <---> | (YouTube API, OpenAI) |
+---------+---------+       +-----------+------------+       +-----------------------+
          |                             |
          |         +-------------------+-------------------+
          |         |                   |                   |
          +---> [API Client] ---> [Parsing Service]  ---> [Database]
                                 [Scaling Service]
                                 [AI Services]
```

## Getting Started

### Prerequisites
- **Python 3.10+**
- **API Keys:**
  - YouTube Data API Key
  - OpenAI API Key or Groq API Key (for AI features)
- **FFmpeg:** Required for audio extraction/Whisper features.

### Installation
1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd Recipe
   ```

2. **Setup Backend:**
   ```bash
   cd recipe-scaler-backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure Environment:**
   Create a `.env` file in `recipe-scaler-backend/` based on `.env.example`:
   ```env
   YOUTUBE_API_KEY=your_key_here
   OPENAI_API_KEY=your_key_here
   GROQ_API_KEY=your_key_here
   ```

### Running the Project
1. **Start the Backend:**
   ```bash
   cd recipe-scaler-backend
   python main.py
   ```
   The API will be available at `http://localhost:8000`. Documentation at `/api/docs`.

2. **Launch the Frontend:**
   Simply open `recipe scaler/index.html` in any modern web browser or serve it using a local HTTP server (e.g., Live Server in VS Code).

## API Endpoints
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/youtube/search` | Search YouTube for recipe videos |
| `POST` | `/api/youtube/extract` | Extract metadata and ingredients from a URL |
| `POST` | `/api/ingredients/parse` | Parse raw text into structured ingredients |
| `POST` | `/api/scaling/scale` | Scale ingredient quantities |
| `POST` | `/api/ai/substitute` | Get AI-powered ingredient substitutions |
| `POST` | `/api/ai/chat` | Chat with the culinary assistant |

## Project Structure
```text
Recipe/
├── recipe scaler/              # Frontend Application
│   ├── index.html              # Main UI
│   ├── api-client.js           # Centralized API Wrapper
│   ├── script.js               # Frontend Logic
│   └── styles.css              # Styling
├── recipe-scaler-backend/      # FastAPI Backend
│   ├── app/
│   │   ├── routes/             # API Endpoints
│   │   ├── services/           # Business Logic
│   │   └── database/           # DB Models & Config
│   ├── main.py                 # Entry Point
│   └── requirements.txt        # Dependencies
└── docs/                       # Migration & Implementation Guides
```

## Author
**Navaneeth**  
[LinkedIn](https://linkedin.com/in/navaneeth-m-545175257) | 
[GitHub](https://github.com/navaneeth0408)
