 CREATE TABLE permission (
    name VARCHAR(50) PRIMARY KEY,
    description TEXT
);

INSERT INTO permission (name, description) VALUES
    ('can_submit_score', 'Allows submitting scores for a game'),
    ('can_view_leaderboard', 'Allows viewing the leaderboard'),
    ('can_view_report', 'Allows accessing analytical reports'),
    ('can_manage_game', 'Allows creating and managing games'),
    ('can_manage_user', 'Allows managing user accounts'),
    ('can_manage_leaderboard', 'Allows managing leaderboards'),
    ('can_manage_score', 'Allows managing scores');

CREATE TABLE user (
    user_id UUID PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE,
    full_name VARCHAR(100),
    country CHAR(2),
    type VARCHAR(10) CHECK (type IN ('individual', 'team')),
    team_member JSONB,
    total_score INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    permission JSONB DEFAULT '["can_submit_score", "can_view_leaderboard"]',
    CONSTRAINT valid_permissions CHECK (permission <@ (SELECT jsonb_agg(name) FROM permission))
);
