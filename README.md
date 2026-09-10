# 🤖 EduBot – AI-Powered Learning Assistant

EduBot is an **AI-powered educational assistant** designed to help students learn, clarify doubts, and interact with educational content through an intuitive conversational interface.

The application combines **AI-powered question answering, interactive learning, and a modern web interface** to provide students with personalized and accessible learning support.

---

## 🚀 Features

* 🤖 **AI Learning Assistant** – Ask questions and receive AI-generated explanations.
* 💬 **Conversational Interface** – Interact with EduBot through a simple chat interface.
* 📚 **Personalized Learning Support** – Get explanations based on the learner's questions and requirements.
* 📝 **Doubt Clarification** – Helps students understand difficult concepts in simple language.
* 🌐 **Responsive UI** – Works across desktop and mobile screen sizes.
* ⚡ **Real-Time Interaction** – Provides responses dynamically through API integration.
* 🔐 **Secure API Integration** – Sensitive API credentials are stored using environment variables.

---

## 🏗️ System Architecture

```text
                👨‍🎓 Student
                    │
                    ▼
          ┌──────────────────┐
          │  React Frontend  │
          │   User Interface │
          └────────┬─────────┘
                   │
              HTTP / REST API
                   │
                   ▼
          ┌──────────────────┐
          │ Backend / API    │
          │ Business Logic   │
          └────────┬─────────┘
                   │
                   ▼
          ┌──────────────────┐
          │   AI Service     │
          │  Response Engine │
          └────────┬─────────┘
                   │
                   ▼
             AI Response
                   │
                   ▼
          React Chat Interface
```

---

## 🛠️ Tech Stack

### Frontend

* React
* JavaScript / TypeScript
* HTML
* CSS
* Vite

### Backend

* Python
* FastAPI
* REST APIs

### AI

* Generative AI / LLM API
* Prompt-based response generation

### Development Tools

* Git
* GitHub
* VS Code

---

## 🔄 How It Works

1. The student enters a question in the EduBot interface.
2. The React frontend captures the user's query.
3. The query is sent to the backend through a REST API.
4. The backend validates and processes the request.
5. The request is sent to the AI model.
6. The AI generates an educational response.
7. The backend returns the response to the frontend.
8. EduBot displays the response in the chat interface.

```text
Student Question
       ↓
React Frontend
       ↓
REST API
       ↓
Backend
       ↓
AI / LLM
       ↓
Generated Explanation
       ↓
React UI
       ↓
Student
```

---

## 📂 Project Structure

```text
EduBot/
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── ...
│
├── backend/
│   ├── app/
│   ├── requirements.txt
│   └── ...
│
├── .env.example
├── .gitignore
└── README.md
```

---

## ⚙️ Installation & Setup

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd EduBot
```

### 2. Setup Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend will run on:

```text
http://localhost:5173
```

### 3. Setup Backend

Open another terminal:

```bash
cd backend

python -m venv venv
```

Activate the virtual environment on Windows:

```powershell
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file and add your required API configuration:

```env
AI_API_KEY=your_api_key_here
```

Start the backend:

```bash
uvicorn app.main:app --reload
```

The backend will run on:

```text
http://localhost:8000
```

API documentation:

```text
http://localhost:8000/docs
```

---

## 🔐 Environment Variables

Never commit API keys or secrets to GitHub.

Create a `.env` file locally:

```env
AI_API_KEY=your_api_key_here
```

Add `.env` to `.gitignore`:

```text
.env
venv/
node_modules/
__pycache__/
```

---

## 🎯 Use Cases

EduBot can be used for:

* Student doubt clarification
* Concept explanations
* Learning assistance
* Programming-related questions
* Exam preparation
* Quick educational guidance
* Interactive self-learning

---

## 🔮 Future Enhancements

* 🎙️ Voice-based interaction
* 🌐 Multilingual learning support
* 📄 PDF/document-based question answering
* 🧠 Personalized learning recommendations
* 📊 Student learning analytics
* 📝 AI-generated quizzes and assessments
* 📚 Course and subject-wise learning
* 🔊 Text-to-Speech responses

---

## 👩‍💻 Developer

**Baavana M**

Information Technology Student
Interested in **Software Development, AI, Automation, and LLM Engineering**.

---

## ⭐ Project Goal

The goal of EduBot is to make learning **more interactive, accessible, and personalized** by combining modern web technologies with generative AI.
