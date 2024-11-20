from typing import Optional, List, Deque
from collections import deque
import time
from EntityResponseCacheClass import EntityResponseCache
from logger import logger
from CodeEntityClass import CodeEntity
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)


class ImprovedRateLimitedGeminiProcessor:
    def __init__(self, gemini_model, 
                 requests_per_minute: int = 30,
                 max_retries: int = 5,
                 cooldown_period: int = 120):
        self.gemini_model = gemini_model
        self.max_retries = max_retries
        self.requests_per_minute = requests_per_minute
        self.cooldown_period = cooldown_period
        self.request_times: Deque[float] = deque(maxlen=requests_per_minute)
        self.consecutive_failures = 0
        self.last_success_time = time.time()
        self.response_cache = EntityResponseCache()

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=2, min=4, max=30),
        retry=retry_if_exception_type(Exception)
    )
    def process_entity(self, entity: CodeEntity) -> Optional[str]:
        """Process a single entity with caching"""
        try:
            # Check cache first
            cached_response = self.response_cache.get_response(entity)
            if cached_response:
                logger.info(f"Using cached response for entity: {entity.name}")
                return cached_response

            # Check if we should process based on previous attempts
            if not self.response_cache.should_process(entity, self.max_retries):
                logger.warning(f"Skipping entity {entity.name} due to previous failures")
                return None

            if self._should_enter_cooldown():
                self._handle_cooldown()
            
            self._enforce_rate_limit()
            
            if entity.type == 'function':
                prompt = self._create_function_analysis_prompt(entity)
            elif entity.type == 'struct':
                prompt = self._create_struct_analysis_prompt(entity)
            else:
                return None
            
            response = self.gemini_model.generate_content(prompt)
            
            # Reset failure counter on success
            self.consecutive_failures = 0
            self.last_success_time = time.time()
            
            # Cache the successful response
            self.response_cache.save_response(entity, response.text)
            
            return response.text
            
        except Exception as e:
            self.consecutive_failures += 1
            self.response_cache.mark_failed(entity, self.consecutive_failures)
            if "429" in str(e):
                logger.warning(f"Rate limit hit for entity {entity.name}, attempt {self.consecutive_failures}")
            raise

    def process_entities_batch(self, entities: List[CodeEntity]) -> None:
        """Process entities with dynamic batch sizing and caching"""
        remaining_entities = list(entities)
        batch_size = 10
        
        while remaining_entities:
            if self.consecutive_failures > 0:
                batch_size = max(3, batch_size // 2)
            elif self.consecutive_failures == 0 and batch_size < 10:
                batch_size += 1
            
            current_batch = remaining_entities[:batch_size]
            remaining_entities = remaining_entities[batch_size:]
            
            successful_count = 0
            for entity in current_batch:
                try:
                    # Skip if already processed successfully
                    if hasattr(entity, 'description') and entity.description:
                        logger.info(f"Entity already has description: {entity.name}")
                        successful_count += 1
                        continue

                    # Check cache before processing
                    cached_response = self.response_cache.get_response(entity)
                    if cached_response:
                        entity.description = cached_response
                        entity.metadata['gemini_analysis'] = cached_response
                        logger.info(f"Using cached response for: {entity.name}")
                        successful_count += 1
                        continue
                        
                    result = self.process_entity(entity)
                    if result:
                        entity.description = result
                        entity.metadata['gemini_analysis'] = result
                        logger.info(f"Successfully processed entity: {entity.name}")
                        successful_count += 1
                    else:
                        logger.warning(f"Skipped processing entity: {entity.name}")
                        
                except Exception as e:
                    logger.error(f"Failed to process entity {entity.name}: {str(e)}")
                    if "RetryError" not in str(e):
                        remaining_entities.append(entity)
            
            delay = 2 if successful_count == len(current_batch) else 5
            logger.info(f"Batch completed. Waiting {delay} seconds before next batch...")
            time.sleep(delay)

    def _enforce_rate_limit(self):
        """Enhanced rate limit checking with adaptive backoff"""
        current_time = time.time()
        
        # Remove old requests
        while self.request_times and current_time - self.request_times[0] >= 60:
            self.request_times.popleft()
        
        # Check if we're at the limit
        if len(self.request_times) >= self.requests_per_minute:
            wait_time = 60 - (current_time - self.request_times[0])
            if wait_time > 0:
                logger.info(f"Rate limit reached, waiting {wait_time:.2f} seconds")
                time.sleep(wait_time + 1)  # Add 1 second buffer
        
        # Add additional backoff if we've had recent failures
        if self.consecutive_failures > 0:
            backoff = min(self.consecutive_failures * 2, 30)  # Max 30 second backoff
            logger.info(f"Adding backoff of {backoff} seconds due to recent failures")
            time.sleep(backoff)
        
        self.request_times.append(current_time)

    def _should_enter_cooldown(self) -> bool:
        """Determine if we should enter cooldown mode"""
        return (self.consecutive_failures >= 3 or 
                (time.time() - self.last_success_time) > 300)  # 5 minutes without success

    def _handle_cooldown(self):
        """Handle cooldown period"""
        logger.warning(f"Entering cooldown period for {self.cooldown_period} seconds")
        time.sleep(self.cooldown_period)
        self.consecutive_failures = 0
        self.request_times.clear()


    def _create_function_analysis_prompt(self, entity: CodeEntity) -> str:
        """Create analysis prompt for function entity"""
        return f"""
        Analyze this RDK function:
        
        Function Name: {entity.name}
        Component: {entity.component}
        Return Type: {entity.metadata.get('return_type', 'Unknown')}
        Parameters: {', '.join(entity.metadata.get('parameters', []))}
        
        Code:
        {entity.content}
        
        Please provide a concise analysis covering:
        1. Main purpose and functionality
        2. Key operations and data flow
        3. Interaction with other components (if any)
        4. Important parameters and return values
        5. Any specific RDK-related operations
        """

    def _create_struct_analysis_prompt(self, entity: CodeEntity) -> str:
        """Create analysis prompt for struct entity"""
        return f"""
        Analyze this RDK structure:
        
        Structure Name: {entity.name}
        Component: {entity.component}
        
        Definition:
        {entity.content}
        
        Please provide a concise analysis covering:
        1. Purpose of this structure
        2. Key fields and their significance
        3. Usage context in RDK
        4. Related components or interfaces
        5. Any specific RDK-related details
        """
    

    