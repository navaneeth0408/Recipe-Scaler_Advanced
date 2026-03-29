# Audio Extraction Feature - Visual Reference Guide

## 🎯 Feature Overview Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  Recipe Scaler - Audio Extraction Feature                  │
│                                                             │
│  🎬 YouTube Video → 🎤 Extract Audio → 📝 Ingredients     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## UI Component Layout

### Frontend Button & Stages

```
┌─ Enter YouTube Link ─────────────────────────────┐
│                                                  │
│  ┌──────────────────────────────────────────┐   │
│  │ https://www.youtube.com/watch?v=...      │   │
│  └──────────────────────────────────────────┘   │
│                                                  │
│  ┌─────────────────────────────────────────┐    │
│  │ ┌──────────────┐  ┌────────────────┐   │    │
│  │ │ Fetch        │  │ 🎤 Audio       │   │    │
│  │ │ Ingredients  │  │ Extract        │   │    │
│  │ └──────────────┘  └────────────────┘   │    │
│  └─────────────────────────────────────────┘    │
│                                                  │
│  ┌─ Extraction Progress ──────────────────────┐  │
│  │ ⏳ Downloading video audio...              │  │
│  │ 🎤 Transcribing speech...                 │  │
│  │ 🔍 Extracting ingredients...              │  │
│  └────────────────────────────────────────────┘  │
│                                                  │
└──────────────────────────────────────────────────┘
```

## Processing Pipeline Visual

```
                    START
                      │
                      ▼
                ┌─────────────┐
                │ YouTube URL │
                └──────┬──────┘
                       │
           ┌───────────┴───────────┐
           │                       │
           ▼                       ▼
    ┌────────────────┐    ┌──────────────┐
    │ Description    │    │ Audio Stream │
    │ Available?     │    │ Available?   │
    └────┬───────────┘    └──────┬───────┘
         │                       │
     YES │ NO              YES   │
        │ ├──────────────────┤  │
        │ │                  │  │
        ▼ ▼                  ▼  ▼
      ┌──────────────────────────────┐
      │  Audio Download (yt-dlp)     │
      │  ├─ Get best quality         │
      │  ├─ Convert to WAV           │
      │  └─ Save to /temp            │
      └──────────┬───────────────────┘
                 │
                 ▼
      ┌──────────────────────────────┐
      │  Transcribe (Faster-Whisper) │
      │  ├─ Load base model          │
      │  ├─ Convert speech→text      │
      │  └─ Combine segments         │
      └──────────┬───────────────────┘
                 │
                 ▼
      ┌──────────────────────────────┐
      │  Cache Transcript            │
      │  └─ Store in DB              │
      └──────────┬───────────────────┘
                 │
                 ▼
      ┌──────────────────────────────┐
      │  Filter Ingredient Sentences │
      │  └─ Keyword matching         │
      └──────────┬───────────────────┘
                 │
                 ▼
      ┌──────────────────────────────┐
      │  Parse Ingredients           │
      │  └─ Extract quantity & unit  │
      └──────────┬───────────────────┘
                 │
                 ▼
           ┌──────────────┐
           │ Return JSON  │
           │ Response     │
           └──────┬───────┘
                  │
                  ▼
                 END
```

## Data Flow Diagram

```
┌──────────────────────────────────────────────────────────┐
│                    FRONTEND (Browser)                    │
│  ┌────────────────────────────────────────────────────┐  │
│  │ 1. User enters YouTube URL                        │  │
│  │ 2. Clicks 🎤 Audio button                         │  │
│  │ 3. Shows extraction progress (3 stages)           │  │
│  │ 4. Displays extracted ingredients                 │  │
│  │ 5. Allows recipe scaling                          │  │
│  └────────┬───────────────────────────────────────────┘  │
└───────────┼────────────────────────────────────────────────┘
            │ HTTP POST /api/youtube/extract-audio-ingredients
            │ {youtube_url: "..."}
            │
            ▼
┌──────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI)                     │
│  ┌────────────────────────────────────────────────────┐  │
│  │ Audio Extraction Endpoint                        │  │
│  │ ├─ Validate URL                                  │  │
│  │ ├─ Extract video ID                              │  │
│  │ ├─ Check cache (YouTubeTranscriptDB)             │  │
│  │ ├─ Download audio (AudioService)                 │  │
│  │ ├─ Transcribe (SpeechService)                    │  │
│  │ ├─ Cache transcript                              │  │
│  │ ├─ Filter sentences (IngredientFilterService)    │  │
│  │ ├─ Parse ingredients (IngredientService)         │  │
│  │ └─ Return response                               │  │
│  └────────┬───────────────────────────────────────────┘  │
└───────────┼────────────────────────────────────────────────┘
            │ HTTP 200 OK
            │ {
            │   video_id: "...",
            │   video_title: "...",
            │   transcript: "...",
            │   ingredients: [...],
            │   success: true
            │ }
            │
            ▼
┌──────────────────────────────────────────────────────────┐
│                    FRONTEND (Browser)                    │
│  ├─ Parse response                                      │
│  ├─ Display video title                                │
│  ├─ Show ingredients list                              │
│  └─ Enable scaling controls                            │
└──────────────────────────────────────────────────────────┘
```

## File Organization Tree

```
Recipe/
│
├── recipe scaler/                  [FRONTEND]
│   ├── index.html                  ✏️ Modified
│   ├── script.js                   ✏️ Modified
│   ├── api-client.js               ✏️ Modified
│   ├── styles.css                  ✏️ Modified
│   └── ... other files
│
├── recipe-scaler-backend/          [BACKEND]
│   ├── requirements.txt            ✏️ Modified (+3 packages)
│   │
│   ├── app/
│   │   ├── services/
│   │   │   ├── audio_service.py           ✨ NEW
│   │   │   ├── speech_service.py          ✨ NEW
│   │   │   ├── ingredient_filter_service.py ✨ NEW
│   │   │   └── ... other services
│   │   │
│   │   ├── routes/
│   │   │   ├── youtube.py          ✏️ Modified (+endpoint)
│   │   │   └── ... other routes
│   │   │
│   │   ├── models/
│   │   │   ├── schemas.py          ✏️ Modified (+2 models)
│   │   │   └── ... other models
│   │   │
│   │   └── database/
│   │       ├── db.py               ✏️ Modified (+1 table)
│   │       └── ... other db files
│   │
│   ├── temp/                        📁 Created (auto-cleanup)
│   │
│   ├── main.py                      (no changes)
│   │
│   └── Documentation/               📚 Extensive
│       ├── AUDIO_EXTRACTION_FEATURE.md
│       ├── AUDIO_EXTRACTION_QUICK_START.md
│       ├── AUDIO_EXTRACTION_FAQ.md
│       ├── IMPLEMENTATION_SUMMARY_AUDIO_EXTRACTION.md
│       ├── FILE_STRUCTURE_AUDIO_EXTRACTION.md
│       └── ... reference documents
│
└── Root Documentation/              📚
    ├── AUDIO_EXTRACTION_IMPLEMENTATION_COMPLETE.md
    ├── IMPLEMENTATION_VERIFICATION_CHECKLIST.md
    └── ... other docs
```

## Component Interaction Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                   USER INTERFACE                            │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ index.html                                          │    │
│  │ ├─ Audio button                                    │    │
│  │ ├─ Progress stages display                         │    │
│  │ └─ Results display area                            │    │
│  └──────┬──────────────────────────────────────────────┘    │
└─────────┼───────────────────────────────────────────────────┘
          │ function call
          ▼
┌─────────────────────────────────────────────────────────────┐
│                   JAVASCRIPT LOGIC                          │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ script.js                                           │    │
│  │ ├─ extractAudioIngredients()                       │    │
│  │ ├─ updateExtractionStage()                         │    │
│  │ └─ displayThumbnail()                              │    │
│  └──────┬──────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ api-client.js                                       │    │
│  │ └─ extractAudioIngredients(url)                    │    │
│  └──────┬──────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ styles.css                                          │    │
│  │ ├─ .extraction-stages                              │    │
│  │ ├─ .stage, .stage-icon                             │    │
│  │ └─ @keyframes animations                           │    │
│  └──────┬──────────────────────────────────────────────┘    │
└─────────┼───────────────────────────────────────────────────┘
          │ HTTP POST /api/youtube/extract-audio-ingredients
          ▼
┌─────────────────────────────────────────────────────────────┐
│                   FASTAPI BACKEND                           │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ youtube.py (extract-audio-ingredients endpoint)   │    │
│  │ ├─ Input validation                               │    │
│  │ ├─ Business logic coordination                     │    │
│  │ └─ Response formatting                             │    │
│  └──────┬──────────────────────────────────────────────┘    │
│         │
│    ┌────┴─────┬──────────────┬─────────────────┐            │
│    │           │              │                 │            │
│    ▼           ▼              ▼                 ▼            │
│  ┌────────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ AudioService   │  │ SpeechService│  │ FilterService│     │
│  │ (yt-dlp)       │  │ (Whisper)    │  │ (Keywords)   │     │
│  └────────────────┘  └──────────────┘  └──────────────┘     │
│         │                    │                 │             │
│         └────────┬───────────┴────────────────┘              │
│                  │                                           │
│                  ▼                                           │
│         ┌─────────────────────┐                            │
│         │ IngredientService   │                            │
│         │ (Parser)            │                            │
│         └────────┬────────────┘                            │
│                  │                                           │
│                  ▼                                           │
│         ┌──────────────────────┐                           │
│         │ YouTubeTranscriptDB  │                           │
│         │ (SQLite Cache)       │                           │
│         └──────────────────────┘                           │
└──────────────────────────────────────────────────────────────┘
```

## Error Handling Flow

```
Input URL
    │
    ▼
Is Valid YouTube URL?
    ├─ NO  → Return: "Invalid YouTube URL" (400)
    └─ YES
         │
         ▼
    Extract Video ID
         │
         ▼
    Is ID Valid?
         ├─ NO  → Return: Error (400)
         └─ YES
              │
              ▼
         Check Cache
              │
         ┌────┴────┐
         │          │
        Hit        Miss
         │          │
         │          ▼
         │     Download Audio
         │          │
         │          ▼
         │     Failed?
         │          ├─ YES → Return: Error (500)
         │          └─ NO
         │              │
         │              ▼
         │          Transcribe Audio
         │              │
         │              ▼
         │          Failed?
         │              ├─ YES → Return: Error (500)
         │              └─ NO
         │                  │
         │                  ▼
         │              Cache Transcript
         │              │
         └──────┬───────┘
                │
                ▼
         Filter Ingredients
                │
                ▼
         Found Ingredients?
                ├─ NO  → Return: Warning (200)
                └─ YES
                     │
                     ▼
                 Parse Ingredients
                     │
                     ▼
                 Succeeded?
                     ├─ YES → Return: Results (200)
                     └─ NO  → Return: Error (500)
```

## Database Schema Visualization

```
┌──────────────────────────────────────────────────────┐
│           youtube_transcripts TABLE                 │
├──────────────────────────────────────────────────────┤
│ COLUMN                │ TYPE        │ CONSTRAINTS   │
├──────────────────────────────────────────────────────┤
│ id                   │ VARCHAR     │ PRIMARY KEY   │
│ video_id             │ VARCHAR     │ UNIQUE INDEX  │
│ title                │ VARCHAR     │               │
│ transcript           │ TEXT        │               │
│ transcript_segments  │ JSON        │ NULLABLE      │
│ duration             │ FLOAT       │ NULLABLE      │
│ language             │ VARCHAR     │ DEFAULT "en"  │
│ extraction_method    │ VARCHAR     │               │
│ created_at           │ DATETIME    │ AUTO TS       │
│ updated_at           │ DATETIME    │ AUTO TS       │
└──────────────────────────────────────────────────────┘

Example Row:
┌──────────────────────────────────────────────────────┐
│ id: "abc123..."                                     │
│ video_id: "dQw4w9WgXcQ"                             │
│ title: "Easy Pasta Recipe"                          │
│ transcript: "Today we'll make pasta. Start with..." │
│ duration: 600.5                                     │
│ language: "en"                                      │
│ extraction_method: "audio"                          │
│ created_at: 2026-03-06 10:30:00                    │
│ updated_at: 2026-03-06 10:30:00                    │
└──────────────────────────────────────────────────────┘
```

## Request/Response Cycle

```
CLIENT                                    SERVER
(Browser)                                 (FastAPI)
   │                                          │
   │  POST /api/youtube/extract-audio-ingredients
   │  {                                       │
   │    "youtube_url": "https://..."         │
   │  }                                       │
   ├──────────────────────────────────────→  │
   │                                          │
   │                      [Processing...]     │
   │                      ├─ Download audio  │
   │                      ├─ Transcribe      │
   │                      ├─ Filter          │
   │                      └─ Extract         │
   │                                          │
   │  HTTP 200 OK                            │
   │  {                                       │
   │    "video_id": "dQw4w9WgXcQ",           │
   │    "video_title": "Recipe Name",        │
   │    "transcript": "...",                 │
   │    "ingredients": [                     │
   │      {                                  │
   │        "name": "flour",                 │
   │        "quantity": 2.0,                 │
   │        "unit": "cup",                   │
   │        "notes": null                    │
   │      },                                 │
   │      ...                                │
   │    ],                                   │
   │    "extraction_method": "audio",        │
   │    "success": true                      │
   │  }                                       │
   │  ←────────────────────────────────────┤ │
   │                                         │
   │  [Display Results]                      │
   │  ├─ Show video title                   │
   │  ├─ List ingredients                   │
   │  └─ Enable scaling                     │
   │                                         │
```

## UI State Transitions

```
┌─────────────┐
│   INITIAL   │
│   STATE     │
└──────┬──────┘
       │ User enters URL & clicks Audio
       ▼
┌──────────────────┐
│   PROCESSING     │
│  ⏳ Downloading  │  Stage 1
│  🎤 Transcribing│  Stage 2
│  🔍 Extracting  │  Stage 3
└────┬────────────┘
     │
     ├─ NO WAIT ─→ ┌──────────────┐
     │             │   ERROR      │
     │             │   STATE      │
     │             │   ❌ Error   │
     │             │   Message    │
     │             └──────────────┘
     │
     └─ SUCCESS ──→ ┌──────────────┐
                   │  RESULTS     │
                   │  STATE       │
                   │ ✅ Ingredients
                   │    Listed    │
                   │ 📊 Scaling   │
                   │    Options   │
                   └──────────────┘
```

## Memory & Performance Profile

```
        Memory Usage Over Time
         │
       600 │                    ┌─────────────────
         │                  ╱│ │ Whisper Model
       500 │             ╱   │ │ Loaded
         │           ╱     │ │
       400 │       ╱       │ │
         │   ╱           │ │
       300 │             │ │
         │             │ │
       200 │             │ └─ Temp Audio
         │             │     (Auto-cleaned)
       100 │             │
         │ │             │
         └─┴─────────────┴──────────────────► Time
           Start   Download   Transcribe  End
                   Audio      Complete

Processing Time Comparison
     Chart
      │
    94 │     [First Time - Full Pipeline]
    60 │     █████████████████████
       │     ║ Download + Transc. + Parse
    30 │     
       │
     3 │     [Cached - Fast Path]
       │     ███
       │     ║ Parse only
     1 │     
       │
     0 └─────────────────────────────────────
       First Time  Second Time (Cached)
```

---

**Visual Reference Complete** ✓

Use these diagrams to understand the feature architecture, data flow, and component interactions.
