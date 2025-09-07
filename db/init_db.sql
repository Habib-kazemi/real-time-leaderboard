-- Table: permission
CREATE TABLE IF NOT EXISTS permission (
    name VARCHAR(50) PRIMARY KEY,
    description TEXT
);

-- Insert initial permissions
INSERT INTO permission (name, description) VALUES
    ('can_submit_score', 'Allows submitting scores for a game'),
    ('can_view_leaderboard', 'Allows viewing the leaderboard'),
    ('can_view_report', 'Allows accessing analytical reports'),
    ('can_manage_game', 'Allows creating and managing games'),
    ('can_manage_user', 'Allows managing user accounts'),
    ('can_manage_leaderboard', 'Allows managing leaderboards'),
    ('can_manage_score', 'Allows managing scores')
ON CONFLICT (name) DO NOTHING;

-- Table: users (renamed from "user")
CREATE TABLE IF NOT EXISTS users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE,
    full_name VARCHAR(100),
    country CHAR(2),
    type VARCHAR(10) NOT NULL CHECK (type IN ('individual', 'team')),
    team_member JSONB DEFAULT '[]'::jsonb,
    total_score INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    permission JSONB DEFAULT '["can_submit_score", "can_view_leaderboard"]'::jsonb
);

-- Table: game
CREATE TABLE IF NOT EXISTS game (
    game_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    category VARCHAR(50),
    active BOOLEAN DEFAULT TRUE,
    max_score INTEGER,
    min_score INTEGER DEFAULT 0,
    play_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    leaderboard_enabled BOOLEAN DEFAULT TRUE,
    team_allowed BOOLEAN DEFAULT TRUE
);

-- Table: score (updated to reference users table)
CREATE TABLE IF NOT EXISTS score (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(user_id),
    game_id VARCHAR(50) NOT NULL REFERENCES game(game_id),
    score INTEGER NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    session_id UUID UNIQUE NOT NULL,
    is_record BOOLEAN DEFAULT FALSE,
    device VARCHAR(50)
);

-- Table: global_record (updated to reference users table)
CREATE TABLE IF NOT EXISTS global_record (
    id SERIAL PRIMARY KEY,
    game_id VARCHAR(50) NOT NULL REFERENCES game(game_id),
    user_id UUID NOT NULL REFERENCES users(user_id),
    username VARCHAR(50) NOT NULL,
    score INTEGER NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    session_id UUID NOT NULL,
    CONSTRAINT unique_game_record UNIQUE (game_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_score_user_id ON score(user_id);
CREATE INDEX IF NOT EXISTS idx_score_game_id ON score(game_id);
CREATE INDEX IF NOT EXISTS idx_global_record_game_id ON global_record(game_id);

-- Function to validate permission JSONB array
CREATE OR REPLACE FUNCTION validate_permissions() RETURNS TRIGGER AS $$
BEGIN
    IF NEW.permission IS NOT NULL THEN
        PERFORM 1
        FROM jsonb_array_elements_text(NEW.permission) AS perm
        WHERE perm NOT IN (SELECT name FROM permission);
        IF FOUND THEN
            RAISE EXCEPTION 'Invalid permission found in permission JSONB array';
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to validate permissions on insert or update
CREATE TRIGGER check_permissions
BEFORE INSERT OR UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION validate_permissions();