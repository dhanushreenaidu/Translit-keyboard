# # backend/src/services/chat_service.py

# from __future__ import annotations

# from typing import Optional, List

# from ..schemas.chat import ChatMessage, ChatRequest, ChatResponse
# from ..config.settings import settings

# # Make Gemini optional so backend still runs without the package
# try:
#     import google.generativeai as genai  # type: ignore
# except ImportError:
#     genai = None


# class ChatService:
#     """
#     Chat service that can work in two modes:
#     - stub  : local fake assistant (no internet, no cost)
#     - gemini: real LLM using Google Gemini API
#     """

#     def __init__(self) -> None:
#         self.provider = settings.CHAT_PROVIDER.lower()
#         self._gemini_model = None

#         if self.provider == "gemini" and settings.GEMINI_API_KEY and genai is not None:
#             genai.configure(api_key=settings.GEMINI_API_KEY)
#             self._gemini_model = genai.GenerativeModel("gemini-2.5-flash")
#             print("[ChatService] Using Gemini provider")
#         else:
#             if self.provider == "gemini" and genai is None:
#                 print(
#                     "[ChatService] CHAT_PROVIDER='gemini' but google.generativeai not installed. Falling back to stub."
#                 )
#             else:
#                 print("[ChatService] Using stub provider")
#             self.provider = "stub"

#     # ------------ PUBLIC API ------------

#     def generate_reply(self, req: ChatRequest) -> ChatResponse:
#         if self.provider == "gemini" and self._gemini_model is not None:
#             try:
#                 return self._generate_with_gemini(req)
#             except Exception as e:
#                 print(f"[ChatService] Gemini error, falling back to stub: {e}")

#         # fallback
#         return self._generate_stub(req)

#     # ------------ STUB MODE ------------

#     def _generate_stub(self, req: ChatRequest) -> ChatResponse:
#         user_msg: Optional[ChatMessage] = None
#         for m in reversed(req.messages):
#             if m.role == "user":
#                 user_msg = m
#                 break

#         if user_msg is None:
#             return ChatResponse(
#                 reply="I didn't receive any user message. Try saying something!",
#                 provider="stub",
#             )

#         lang = req.language.lower()
#         lang_name = {
#             "hi": "Hindi",
#             "te": "Telugu",
#             "ta": "Tamil",
#             "kn": "Kannada",
#             "ml": "Malayalam",
#             "mr": "Marathi",
#             "gu": "Gujarati",
#             "bn": "Bengali",
#             "pa": "Punjabi",
#         }.get(lang, "English / mixed")

#         reply_text = (
#             f"You said: “{user_msg.content}”.\n\n"
#             f"I'm your TransKey assistant working in {lang_name} mode. "
#             f"Right now I'm in stub mode (no real LLM), "
#             f"but the pipeline and UI are the same as a real assistant."
#         )

#         return ChatResponse(reply=reply_text, provider="stub")

#     # ------------ GEMINI MODE ------------

#     def _generate_with_gemini(self, req: ChatRequest) -> ChatResponse:
#         if self._gemini_model is None:
#             return self._generate_stub(req)

#         history = []
#         for m in req.messages:
#             role = "user" if m.role == "user" else "model"
#             history.append({"role": role, "parts": [m.content]})

#         system_prompt = (
#             "You are TransKey, a helpful assistant built on top of a "
#             "multilingual transliteration keyboard app for Indian languages. "
#             "Be concise and friendly. When helpful, explain how ML, "
#             "transliteration, or Indic languages relate to the user's query. "
#             f"The user has currently selected language code: {req.language}."
#         )

#         chat_session = self._gemini_model.start_chat(history=history)
#         response = chat_session.send_message(system_prompt)

#         text = getattr(response, "text", None)
#         if not text:
#             try:
#                 text = response.candidates[0].content.parts[0].text
#             except Exception:
#                 text = "Sorry, I couldn't generate a response."

#         return ChatResponse(reply=text, provider="gemini")


# chat_service = ChatService()


from __future__ import annotations

from typing import Optional, List

from ..schemas.chat import ChatMessage, ChatRequest, ChatResponse
from ..config.settings import settings

# Make Gemini optional so backend still runs without the package
try:
    import google.generativeai as genai  # type: ignore
except ImportError:
    genai = None


class ChatService:
    """
    Chat service that can work in two modes:
    - stub  : local fake assistant (no internet, no cost)
    - gemini: real LLM using Google Gemini API
    """

    def __init__(self) -> None:
        self.provider = settings.CHAT_PROVIDER.lower()
        self._gemini_model = None

        if self.provider == "gemini" and settings.GEMINI_API_KEY and genai is not None:
            try:
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self._gemini_model = genai.GenerativeModel("gemini-2.5-flash")
                print("[ChatService] Using Gemini provider")
            except Exception as e:
                print(f"[ChatService] Failed to init Gemini: {e}")
                print("[ChatService] Falling back to stub provider")
                self.provider = "stub"
        else:
            if self.provider == "gemini" and genai is None:
                print(
                    "[ChatService] CHAT_PROVIDER='gemini' but google.generativeai "
                    "is not installed. Falling back to stub."
                )
            else:
                print("[ChatService] Using stub provider")
            self.provider = "stub"

    # ------------ PUBLIC API ------------

    def generate_reply(self, req: ChatRequest) -> ChatResponse:
        if self.provider == "gemini" and self._gemini_model is not None:
            try:
                return self._generate_with_gemini(req)
            except Exception as e:
                print(f"[ChatService] Gemini error, falling back to stub: {e}")

        # fallback
        return self._generate_stub(req)

    # ------------ STUB MODE ------------

    def _generate_stub(self, req: ChatRequest) -> ChatResponse:
        user_msg: Optional[ChatMessage] = None
        for m in reversed(req.messages):
            if m.role == "user":
                user_msg = m
                break

        if user_msg is None:
            return ChatResponse(
                reply="I didn't receive any user message. Try saying something!",
                provider="stub",
            )

        lang = req.language.lower()
        lang_name = {
            "hi": "Hindi",
            "te": "Telugu",
            "ta": "Tamil",
            "kn": "Kannada",
            "ml": "Malayalam",
            "mr": "Marathi",
            "gu": "Gujarati",
            "bn": "Bengali",
            "pa": "Punjabi",
        }.get(lang, "English / mixed")

        reply_text = (
            f"You said: “{user_msg.content}”.\n\n"
            f"I'm your TransKey assistant working in {lang_name} mode. "
            f"Right now I'm in stub mode (no real LLM), "
            f"but the pipeline and UI are the same as a real assistant."
        )

        return ChatResponse(reply=reply_text, provider="stub")

    # ------------ GEMINI MODE ------------

    def _generate_with_gemini(self, req: ChatRequest) -> ChatResponse:
        if self._gemini_model is None:
            return self._generate_stub(req)

        # Map our messages to Gemini format
        history: List[dict] = []
        for m in req.messages:
            role = "user" if m.role == "user" else "model"
            history.append({"role": role, "parts": [m.content]})

        system_prompt = (
            "You are TransKey, a helpful assistant built on top of a "
            "multilingual transliteration keyboard app for Indian languages. "
            "Be concise and friendly. When helpful, explain how ML, "
            "transliteration, or Indic languages relate to the user's query. "
            f"The user has currently selected language code: {req.language}."
        )

        chat_session = self._gemini_model.start_chat(history=history)
        response = chat_session.send_message(system_prompt)

        text = getattr(response, "text", None)
        if not text:
            try:
                text = response.candidates[0].content.parts[0].text
            except Exception:
                text = "Sorry, I couldn't generate a response."

        return ChatResponse(reply=text, provider="gemini")


chat_service = ChatService()
