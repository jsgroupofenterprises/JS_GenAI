from RDKAssistant_Class import RDKAssistant

if __name__ == "__main__":
    assistant = RDKAssistant(
        code_base_path=r"C:\Users\39629\Downloads\rdkb_24q1\rdkb_24q1\rdkb\components\opensource\ccsp\OneWifi\lib\common\monitor.c",
        gemini_api_key="AIzaSyAGrz7Fw9flS5OnHu5G-EqvwT1pPVkWV64"
    )
    assistant.initialize()
    assistant.handle_user_interaction()
