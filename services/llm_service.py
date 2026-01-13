"""
LLM Service untuk generate jawaban natural
Mendukung Groq API dan Google Gemini API
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.config import GROQ_CONFIG, GEMINI_CONFIG, CHATBOT_CONFIG


class LLMService:
    """Service untuk LLM (Groq atau Gemini)"""
    
    def __init__(self, provider=None):
        self.provider = provider or CHATBOT_CONFIG['llm_provider']
        self.client = None
        self._init_client()
    
    def _init_client(self):
        """Initialize LLM client based on provider"""
        if self.provider == 'groq':
            self._init_groq()
        elif self.provider == 'gemini':
            self._init_gemini()
        else:
            raise ValueError(f"Unknown LLM provider: {self.provider}")
    
    def _init_groq(self):
        """Initialize Groq client"""
        try:
            from groq import Groq
            
            api_key = GROQ_CONFIG['api_key']
            if not api_key:
                raise ValueError("GROQ_API_KEY not set in environment")
            
            self.client = Groq(api_key=api_key)
            self.model = GROQ_CONFIG['model']
            print(f"Groq client initialized with model: {self.model}")
        except ImportError:
            raise ImportError("Please install groq: pip install groq")
    
    def _init_gemini(self):
        """Initialize Google Gemini client"""
        try:
            import google.generativeai as genai
            
            api_key = GEMINI_CONFIG['api_key']
            if not api_key:
                raise ValueError("GEMINI_API_KEY not set in environment")
            
            genai.configure(api_key=api_key)
            self.client = genai.GenerativeModel(GEMINI_CONFIG['model'])
            self.model = GEMINI_CONFIG['model']
            print(f"Gemini client initialized with model: {self.model}")
        except ImportError:
            raise ImportError("Please install google-generativeai: pip install google-generativeai")
    
    def generate_response(self, user_question: str, faq_context: list, chat_history: list = None) -> str:
        """
        Generate jawaban natural berdasarkan FAQ context
        
        Args:
            user_question: Pertanyaan dari user
            faq_context: List of matched FAQs dengan format:
                [{'question': '...', 'answer': '...', 'similarity': 0.8}, ...]
            chat_history: Optional list of previous messages
            
        Returns:
            Generated response string
        """
        # Build context from matched FAQs
        context_parts = []
        for i, faq in enumerate(faq_context, 1):
            context_parts.append(f"""FAQ {i}:
Q: {faq['question']}
A: {faq['answer']}
Relevansi: {faq.get('similarity', 0):.2%}""")
        
        faq_context_str = "\n\n".join(context_parts) if context_parts else "Tidak ada FAQ yang relevan ditemukan."
        
        # Build the prompt
        prompt = f"""{CHATBOT_CONFIG['system_prompt']}

=== KONTEKS FAQ ===
{faq_context_str}

=== PERTANYAAN PENGGUNA ===
{user_question}

=== INSTRUKSI ===
Berdasarkan FAQ di atas, berikan jawaban yang natural dan informatif dalam Bahasa Indonesia.
Jika FAQ tidak relevan dengan pertanyaan, berikan jawaban umum yang membantu atau sarankan untuk menghubungi petugas.
Jawab dengan singkat, jelas, dan sopan. Jangan menyebutkan nomor FAQ atau skor relevansi."""

        try:
            if self.provider == 'groq':
                return self._generate_groq(prompt, chat_history)
            elif self.provider == 'gemini':
                return self._generate_gemini(prompt, chat_history)
        except Exception as e:
            print(f"Error generating response: {e}")
            return CHATBOT_CONFIG['fallback_message']
    
    def _generate_groq(self, prompt: str, chat_history: list = None) -> str:
        """Generate response using Groq API"""
        messages = []
        
        # Add chat history if available
        if chat_history:
            for msg in chat_history[-6:]:  # Last 6 messages for context
                messages.append({
                    "role": msg['role'],
                    "content": msg['content']
                })
        
        # Add current prompt
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=GROQ_CONFIG['max_tokens'],
            temperature=GROQ_CONFIG['temperature']
        )
        
        return response.choices[0].message.content.strip()
    
    def _generate_gemini(self, prompt: str, chat_history: list = None) -> str:
        """Generate response using Google Gemini API"""
        # Build conversation history
        full_prompt = prompt
        
        if chat_history:
            history_str = "\n".join([
                f"{'User' if msg['role'] == 'user' else 'Assistant'}: {msg['content']}"
                for msg in chat_history[-6:]
            ])
            full_prompt = f"=== RIWAYAT CHAT ===\n{history_str}\n\n{prompt}"
        
        response = self.client.generate_content(
            full_prompt,
            generation_config={
                'max_output_tokens': GEMINI_CONFIG['max_tokens'],
                'temperature': GEMINI_CONFIG['temperature']
            }
        )
        
        return response.text.strip()
    
    def generate_simple_response(self, prompt: str) -> str:
        """Generate simple response tanpa context"""
        try:
            if self.provider == 'groq':
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=512,
                    temperature=0.7
                )
                return response.choices[0].message.content.strip()
            elif self.provider == 'gemini':
                response = self.client.generate_content(prompt)
                return response.text.strip()
        except Exception as e:
            print(f"Error generating simple response: {e}")
            return ""


# Singleton instance
_llm_service = None

def get_llm_service():
    """Get singleton LLM service instance"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service


if __name__ == "__main__":
    # Test LLM service
    service = get_llm_service()
    
    # Test generate response
    faq_context = [
        {
            'question': 'Bagaimana cara mendaftar menjadi anggota perpustakaan?',
            'answer': 'Untuk mendaftar menjadi anggota, silakan datang ke perpustakaan dengan membawa KTP dan foto 3x4.',
            'similarity': 0.85
        }
    ]
    
    response = service.generate_response(
        "Saya mau daftar jadi anggota perpustakaan, gimana caranya?",
        faq_context
    )
    
    print("Response:")
    print(response)
