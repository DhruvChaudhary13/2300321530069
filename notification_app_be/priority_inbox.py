"""
Priority Inbox - Stage 6
Finds top N most important unread notifications based on:
- Type weight (Placement > Result > Event)
- Recency (newer notifications get higher score)
"""

import heapq
from datetime import datetime
from typing import List, Dict, Any

# Import type weights from config
from config import TYPE_WEIGHTS


class PriorityInbox:
    """
    Maintains top N notifications efficiently using Min-Heap.
    O(log N) for insertion, O(1) for retrieving top N.
    
    Fix: Uses counter to break ties when scores are equal.
    """
    
    def __init__(self, n: int = 10):
        """
        Initialize Priority Inbox.
        
        Args:
            n: Number of top notifications to maintain (default: 10)
        """
        self.n = n
        self.heap = []  # Min-heap of (score, counter, notification)
        self.counter = 0  # To break ties when scores are equal
    
    def calculate_priority_score(self, notification: Dict[str, Any]) -> float:
        """
        Calculate priority score for a notification.
        
        Formula: Score = Type_Weight × Recency_Score
        
        Type_Weight: from config (Placement: 3.0, Result: 2.0, Event: 1.0)
        Recency_Score = 1 / (Days_Ago + 1)
        
        Returns:
            Float priority score
        """
        # Get type weight from config
        notification_type = notification.get("Type", "Event")
        type_weight = TYPE_WEIGHTS.get(notification_type, 1.0)
        
        # Calculate days ago
        timestamp_str = notification.get("Timestamp", "")
        try:
            timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
            days_ago = (datetime.now() - timestamp).days
        except (ValueError, TypeError):
            days_ago = 365  # Default to old if parsing fails
        
        # Recency score: newer = higher score
        recency_score = 1.0 / (days_ago + 1)
        
        # Final priority score
        priority_score = type_weight * recency_score
        
        return round(priority_score, 4)
    
    def add_notification(self, notification: Dict[str, Any]) -> None:
        """
        Add a notification to the priority inbox.
        Maintains only top N notifications using min-heap.
        """
        score = self.calculate_priority_score(notification)
        
        notification_with_score = {
            "id": notification.get("ID", ""),
            "type": notification.get("Type", ""),
            "message": notification.get("Message", ""),
            "timestamp": notification.get("Timestamp", ""),
            "priority_score": score
        }
        
        # Use counter to break ties (prevents dict comparison error)
        self.counter += 1
        
        if len(self.heap) < self.n:
            # Push tuple: (score, counter, notification)
            heapq.heappush(self.heap, (score, self.counter, notification_with_score))
        else:
            # Check if this notification has higher score than smallest in heap
            if score > self.heap[0][0]:
                heapq.heapreplace(self.heap, (score, self.counter, notification_with_score))
    
    def add_notifications(self, notifications: List[Dict[str, Any]]) -> None:
        """Add multiple notifications at once."""
        for notification in notifications:
            self.add_notification(notification)
    
    def get_top_n(self) -> List[Dict[str, Any]]:
        """
        Get top N notifications sorted by priority (highest first).
        """
        # Extract notifications from heap (ignore score and counter)
        all_notifications = [item[2] for item in self.heap]
        
        # Sort by priority score descending
        sorted_notifications = sorted(
            all_notifications,
            key=lambda x: x["priority_score"],
            reverse=True
        )
        
        # Add rank
        for i, notif in enumerate(sorted_notifications, 1):
            notif["rank"] = i
        
        return sorted_notifications
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about current inbox."""
        if not self.heap:
            return {"total_in_inbox": 0, "highest_score": 0, "lowest_score": 0}
        
        scores = [item[0] for item in self.heap]  # Extract scores from tuple
        return {
            "total_in_inbox": len(self.heap),
            "highest_score": max(scores),
            "lowest_score": min(scores)
        }


def get_top_priority_notifications(notifications: List[Dict[str, Any]], n: int = 10) -> List[Dict[str, Any]]:
    """
    Convenience function to get top N priority notifications.
    """
    inbox = PriorityInbox(n)
    inbox.add_notifications(notifications)
    return inbox.get_top_n()