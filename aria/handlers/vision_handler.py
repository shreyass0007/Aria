import logging

logger = logging.getLogger(__name__)

class VisionHandler:
    def __init__(self, tts_manager, brain, vision_pipeline_factory):
        self.tts_manager = tts_manager
        self.brain = brain
        self.get_pipeline = vision_pipeline_factory

    def handle(self, text, intent, parameters):
        self.tts_manager.speak("Taking a look at your screen...")
        
        try:
            # Get the pipeline (lazy initialization via factory)
            pipeline = self.get_pipeline()
            if not pipeline:
                self.tts_manager.speak("Vision system is not available.")
                return "Vision pipeline failed to initialize."
            
            logger.info("Analyzing screen...")
            # Analyze screen
            result = pipeline.analyze_screen(save_debug=True)
            
            if "error" in result:
                msg = f"Vision error: {result['error']}"
                logger.error(msg)
                self.tts_manager.speak("Sorry, I had trouble seeing the screen.")
                return msg
            
            # Format the visual data for the LLM
            # result contains 'objects', 'text', 'ui_elements' etc. from LayoutAnalyzer
            
            # We want to describe what we see.
            # Construct a prompt context
            context_data = {
                "detected_objects": [obj['label'] for obj in result.get('objects', [])],
                "detected_text": result.get('text_content', ''), # LayoutAnalyzer usually aggregates text
                "summary": result.get('summary', '') # If LayoutAnalyzer produces a summary
            }
            
            # If LayoutAnalyzer isn't fully implemented to give a summary, we use raw data
            if not context_data['detected_text']:
                 # Fallback to raw text list if text_content disjoint
                 context_data['detected_text'] = " ".join([t['text'] for t in result.get('ocr_results', [])])

            prompt = f"""
            You are Aria's visual cortex. 
            User Query: "{text}"
            
            Here is what is currently on the computer screen:
            OBJECTS: {context_data['detected_objects']}
            TEXT CONTENT: {context_data['detected_text']}
            
            Based on this visual data, answer the user's query or describe the screen.
            Be concise and natural.
            """
            
            logger.info("Asking Brain to describe screen...")
            response = self.brain.ask(prompt)
            
            self.tts_manager.speak(response)
            return response

        except Exception as e:
            logger.error(f"Error in VisionHandler: {e}", exc_info=True)
            self.tts_manager.speak("Something went wrong while trying to see.")
            return f"Error processing vision command: {str(e)}"
