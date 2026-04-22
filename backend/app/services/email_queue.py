"""
Email Queue Service - Handles asynchronous email sending using a queue.
This prevents email sending from blocking the main request/response cycle.
"""
import asyncio
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class EmailTask:
    """Email task to be processed by the queue."""
    recipients: list[str]
    subject: str
    body: str
    subtype: str = "html"
    task_id: Optional[str] = None
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.task_id is None:
            import uuid
            self.task_id = str(uuid.uuid4())


class EmailQueue:
    """Email queue for asynchronous email processing."""
    
    def __init__(self, max_workers: int = 3, max_queue_size: int = 1000):
        """
        Initialize email queue.
        
        Args:
            max_workers: Maximum number of concurrent email workers
            max_queue_size: Maximum queue size before rejecting new tasks
        """
        self.queue: asyncio.Queue = asyncio.Queue(maxsize=max_queue_size)
        self.max_workers = max_workers
        self.workers: list[asyncio.Task] = []
        self.is_running = False
        self.processed_count = 0
        self.failed_count = 0
        self._email_service = None
    
    def set_email_service(self, email_service):
        """Set the email service instance to use for sending emails."""
        self._email_service = email_service
    
    async def enqueue(
        self,
        recipients: list[str],
        subject: str,
        body: str,
        subtype: str = "html"
    ) -> str:
        """
        Add an email task to the queue.
        
        Args:
            recipients: List of email recipients
            subject: Email subject
            body: Email body
            subtype: Email subtype (html or plain)
            
        Returns:
            Task ID for tracking
            
        Raises:
            asyncio.QueueFull: If queue is full
        """
        task = EmailTask(
            recipients=recipients,
            subject=subject,
            body=body,
            subtype=subtype
        )
        
        try:
            await self.queue.put(task)
            logger.info(f"Email task {task.task_id} enqueued for {recipients}")
            return task.task_id
        except asyncio.QueueFull:
            logger.error(f"Email queue is full. Failed to enqueue email to {recipients}")
            self.failed_count += 1
            raise
    
    async def _worker(self, worker_id: int):
        """Background worker that processes email tasks from the queue."""
        logger.info(f"Email worker {worker_id} started")
        
        while self.is_running:
            try:
                # Wait for a task with timeout to allow checking is_running
                try:
                    task = await asyncio.wait_for(self.queue.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue
                
                if task is None:  # Poison pill to stop worker
                    break
                
                # Process the email task
                if self._email_service:
                    try:
                        success = await self._email_service._send_email_direct(
                            recipients=task.recipients,
                            subject=task.subject,
                            body=task.body,
                            subtype=task.subtype
                        )
                        
                        if success:
                            self.processed_count += 1
                            logger.info(
                                f"Worker {worker_id}: Email sent successfully "
                                f"(task {task.task_id}) to {task.recipients}"
                            )
                        else:
                            self.failed_count += 1
                            logger.warning(
                                f"Worker {worker_id}: Email sending failed "
                                f"(task {task.task_id}) to {task.recipients}"
                            )
                    except Exception as e:
                        self.failed_count += 1
                        logger.error(
                            f"Worker {worker_id}: Error processing email task "
                            f"{task.task_id}: {e}",
                            exc_info=True
                        )
                else:
                    logger.error("Email service not set in queue")
                    self.failed_count += 1
                
                # Mark task as done
                self.queue.task_done()
                
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}", exc_info=True)
                await asyncio.sleep(1)  # Prevent tight error loop
        
        logger.info(f"Email worker {worker_id} stopped")
    
    async def start(self):
        """Start the email queue workers."""
        if self.is_running:
            logger.warning("Email queue is already running")
            return
        
        if not self._email_service:
            logger.error("Cannot start email queue: email service not set")
            return
        
        self.is_running = True
        self.workers = [
            asyncio.create_task(self._worker(i))
            for i in range(self.max_workers)
        ]
        logger.info(f"Email queue started with {self.max_workers} workers")
    
    async def stop(self, timeout: float = 30.0):
        """Stop the email queue workers gracefully."""
        if not self.is_running:
            return
        
        logger.info("Stopping email queue workers...")
        self.is_running = False
        
        # Add poison pills to stop workers
        for _ in range(self.max_workers):
            await self.queue.put(None)
        
        # Wait for workers to finish with timeout
        try:
            await asyncio.wait_for(
                asyncio.gather(*self.workers, return_exceptions=True),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            logger.warning("Email workers did not stop within timeout, cancelling...")
            for worker in self.workers:
                worker.cancel()
        
        # Wait for queue to be empty
        await self.queue.join()
        
        logger.info(
            f"Email queue stopped. Processed: {self.processed_count}, "
            f"Failed: {self.failed_count}"
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get queue statistics."""
        return {
            "is_running": self.is_running,
            "queue_size": self.queue.qsize(),
            "max_workers": self.max_workers,
            "active_workers": len([w for w in self.workers if not w.done()]),
            "processed_count": self.processed_count,
            "failed_count": self.failed_count
        }


# Global email queue instance
_email_queue: Optional[EmailQueue] = None


def get_email_queue() -> EmailQueue:
    """Get the global email queue instance."""
    global _email_queue
    if _email_queue is None:
        _email_queue = EmailQueue(max_workers=3, max_queue_size=1000)
    return _email_queue

