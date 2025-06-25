import logging
import asyncio

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message

logger = logging.getLogger(__name__)

class EnhancedAgent:
    """Enhanced agent that processes actual user messages."""

    async def invoke(self, message: str) -> str:
        """Process a message and return response."""
        logger.info(f"Agent processing message: {message}")
        
        # Simulate some processing time
        await asyncio.sleep(0.5)
        
        # Different responses based on input
        if "hello" in message.lower():
            return "Hello! Nice to meet you through the A2A protocol!"
        elif "time" in message.lower():
            return "I don't have access to real time, but I can process your requests!"
        elif "error" in message.lower():
            raise Exception("Simulated error for testing error handling")
        else:
            return f"I received your message: '{message}'. How can I help you?"
    
    
class EnhancedAgentExecutor(AgentExecutor):
    """
    Enhanced Agent Executor that processes actual user input.
    
    Key improvements over official example:
    1. Extracts user message from RequestContext
    2. Processes the actual message content
    3. Detailed logging for learning
    4. Error handling
    """

    def __init__(self):
        self.agent = EnhancedAgent()
        logger.info("Enhanced AgentExecutor initialized")

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        """
        Enhanced execution with message processing.
        """
        logger.info("=== Enhanced AgentExecutor.execute() called ===")
        
        # Extract message from RequestContext
        user_message = self._extract_message_from_context(context)
        logger.info(f"Extracted user message: {user_message}")
        
        # Log context details for learning
        self._log_context_details(context)
        
        try:
            # Process with enhanced agent
            logger.info("Calling enhanced agent.invoke()...")
            result = await self.agent.invoke(user_message)
            logger.info(f"Agent returned: {result}")
            
            # Enqueue the response
            logger.info("Enqueueing response to EventQueue...")
            await event_queue.enqueue_event(new_agent_text_message(result))
            logger.info("✅ Response successfully enqueued!")
            
        except Exception as e:
            # Handle errors gracefully
            error_msg = f"Agent execution failed: {str(e)}"
            logger.error(error_msg)
            await event_queue.enqueue_event(new_agent_text_message(error_msg))

    async def cancel(
        self, 
        context: RequestContext, 
        event_queue: EventQueue
    ) -> None:
        """Enhanced cancel with proper response."""
        logger.info("=== Enhanced AgentExecutor.cancel() called ===")
        cancel_msg = "Agent execution was cancelled"
        await event_queue.enqueue_event(new_agent_text_message(cancel_msg))

    def _extract_message_from_context(self, context: RequestContext) -> str:
        """Extract user message from RequestContext."""
        if not context.message:
            return "No message found"
            
        if context.message.parts:
            for part in context.message.parts:
                # A2A SDK structure: Part(root=TextPart(text='hello'))
                if hasattr(part, 'root') and hasattr(part.root, 'text'):
                    return part.root.text
                elif hasattr(part, 'text'):
                    return part.text
        return "No message found"

    def _log_context_details(self, context: RequestContext):
        """Log RequestContext details for learning purposes."""
        logger.info("--- RequestContext Details ---")
        logger.info(f"Message ID: {context.message.messageId if context.message else 'None'}")
        logger.info(f"Message Role: {context.message.role if context.message else 'None'}")
        logger.info(f"Message Parts Count: {len(context.message.parts) if context.message and context.message.parts else 0}")
        logger.info(f"Task ID: {context.task_id}")
        logger.info("-----------------------------")