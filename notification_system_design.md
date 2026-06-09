# Notification System Design Document

## Stage 1: REST API Design

### Core Actions
- Get notifications (all/unread)
- Mark as read (single/all)
- Delete notifications
- Get unread count
- Real-time notifications

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/notifications | Get all notifications |
| GET | /api/notifications?unread=true | Get unread only |
| GET | /api/notifications/unread/count | Get unread count |
| PUT | /api/notifications/:id/read | Mark as read |
| PUT | /api/notifications/read-all | Mark all as read |
| DELETE | /api/notifications/:id | Delete notification |

### Real-time Mechanism: WebSockets
- Full-duplex communication
- Low latency (~10ms)
- Automatic reconnection handling

## Stage 2: Database Design

### Database: PostgreSQL
- ACID compliance for critical data
- Excellent JSON support
- Strong indexing capabilities

### Schema

```sql
CREATE TABLE students (
    id BIGSERIAL PRIMARY KEY,
    roll_number VARCHAR(20) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id BIGINT REFERENCES students(id),
    notification_type VARCHAR(20) CHECK (type IN ('Placement', 'Result', 'Event')),
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_student_read ON notifications(student_id, is_read);
CREATE INDEX idx_created_at ON notifications(created_at DESC);


Original Slow Query
sql
SELECT * FROM notifications
WHERE studentID = 1042 AND isRead = false
ORDER BY createdAt DESC;

Optimized Solution
sql
-- Add composite index
CREATE INDEX idx_student_unread_created 
ON notifications(studentID, isRead, createdAt DESC);

Optimized query

SELECT id, type, message, created_at
FROM notifications
WHERE studentID = 1042 AND isRead = false
ORDER BY createdAt DESC;
Index Every Column? NO
Each index slows INSERT/UPDATE/DELETE

Wasted disk space

Only index columns used in WHERE/ORDER BY