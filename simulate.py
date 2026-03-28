#!/usr/bin/env python3
"""
Sadhana Mitra — Interactive Simulation Mode
=============================================
Run this to chat with the bot in your terminal. No API keys needed.

Usage:
    python simulate.py

Type your messages as a Sadhak would on WhatsApp.
Type 'quit' or 'exit' to end the session.
"""

from app.bot import generate_response


BANNER = """
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║          🙏  SADHANA MITRA — Simulation Mode  🙏          ║
║                                                          ║
║   WhatsApp Bot for Saadho Sangha                         ║
║   Type messages as a Sadhak would on WhatsApp.           ║
║                                                          ║
║   Commands:                                              ║
║     quit / exit  — End session                           ║
║     menu         — Show the main menu                    ║
║     help         — Show this help                        ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
"""

SAMPLE_QUERIES = """
  Try these sample messages:
  ─────────────────────────────────────
  • Hi
  • Namaste
  • 1  (or any number 1-7)
  • What yoga classes do you offer?
  • How can I visit the Ashram?
  • I want to volunteer
  • How do I join the Sunday Satsang?
  • Tell me about upcoming retreats
  • How can I meet Gurudev?
  • How can I donate?
  • I need spiritual guidance
  • योग कक्षाएँ कब होती हैं?
  • What is Saadho?
  ─────────────────────────────────────
"""


def main():
    print(BANNER)
    print(SAMPLE_QUERIES)

    while True:
        try:
            user_input = input("\n📱 You (Sadhak): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\n🙏 Namaste! May your path be blessed. 🙏\n")
            break

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit", "q"):
            print("\n🙏 Namaste! May your path be blessed. 🙏\n")
            break

        if user_input.lower() == "help":
            print(SAMPLE_QUERIES)
            continue

        if user_input.lower() == "menu":
            user_input = "Hi"

        # Generate response
        response = generate_response(user_input)

        print(f"\n🤖 Sadhana Mitra:\n{'─' * 50}")
        print(response)
        print(f"{'─' * 50}")


if __name__ == "__main__":
    main()
